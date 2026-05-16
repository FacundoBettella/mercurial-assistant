"""Domain services for content moderation."""

import hashlib
import re
import unicodedata
from datetime import UTC, datetime

from src.domain.entities.moderation_action import ModerationAction
from src.domain.interfaces.log_repository import ILogRepository


class ModerationEvaluator:
    """Stateless domain service: classifies text and hashes PII.

    No dependencies on repositories or external services.
    Fully testable without mocks.
    """

    def __init__(self, salt: str) -> None:
        self._salt = salt

        self._risk_keywords: dict[str, set[str]] = {
            "hate_speech": {"racial slur", "nazi", "matar"},
            "self_harm": {"suicidio", "auto lesion", "cortarme"},
            "violence": {"bomb", "disparar", "asesinar", "asesino"},
            "cyber_abuse": {
                "sql injection",
                "bypass authentication",
                "robo de credenciales",
                "phishing",
            },
        }

        self._adversarial_context_markers = {
            "fingiendo",
            "ficticio",
            "roleplay",
            "hace de cuenta",
            "para una investigacion",
            "para fines educativos",
        }

    def hash_value(self, value: str) -> str:
        return hashlib.sha256(f"{self._salt}:{value}".encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text.lower())
        normalized = re.sub(r"[\W_]+", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    def evaluate(self, text: str) -> tuple[list[str], ModerationAction, str]:
        """Classify text against content policy.

        Returns:
            (detected_risks, action, reason)
        """
        normalized = self._normalize_text(text)
        risks: list[str] = []

        for risk, keywords in self._risk_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                risks.append(risk)

        if risks:
            return risks, ModerationAction.BLOCK, "Explicit risky content detected by keyword/pattern policy."

        if any(marker in normalized for marker in self._adversarial_context_markers) and any(
            token in normalized for token in ["credenciales", "password", "documento", "dni", "user id", "bypass"]
        ):
            return ["prompt_evasion"], ModerationAction.FLAG, "Potential adversarial framing detected for manual review."

        return [], ModerationAction.ALLOW, "No risk detected under current policy."


class ModerationService:
    """Domain service: build + persist audit records.

    Depends only on domain abstractions (ILogRepository).
    Delegates classification to ModerationEvaluator.
    """

    def __init__(self, evaluator: ModerationEvaluator, log_repository: ILogRepository) -> None:
        self._evaluator = evaluator
        self._log_repository = log_repository

    def evaluate(self, text: str) -> tuple[list[str], ModerationAction, str]:
        return self._evaluator.evaluate(text)

    def build_log_record(
        self,
        user_id: str,
        text: str,
        detected_risks: list[str],
        action: ModerationAction,
        request_id: str,
    ) -> dict:
        retention_tag = "clean_30d"
        if action == ModerationAction.FLAG:
            retention_tag = "flagged_event_90d"
        elif action == ModerationAction.BLOCK:
            retention_tag = "incident_365d"

        return {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "request_id": request_id,
            "anonymized_user_id": self._evaluator.hash_value(user_id),
            "input_hash": self._evaluator.hash_value(text),
            "detected_risks": detected_risks,
            "moderation_action": action.value,
            "model_response_id": "resp-local-v1",
            "retention_tag": retention_tag,
        }

    def log_moderation_event(
        self,
        user_id: str,
        text: str,
        detected_risks: list[str],
        action: ModerationAction,
        request_id: str,
    ) -> None:
        record = self.build_log_record(user_id, text, detected_risks, action, request_id)
        self._log_repository.write_log(record)
