"""Core moderation service with dual-filter detection logic."""

import hashlib
from datetime import UTC, datetime
import re
import unicodedata

from .schemas import LogRepository, ModerationAction


class ModerationService:
    """Business logic for content moderation.

    Depends on abstraction (LogRepository), not concrete implementation.
    """

    def __init__(self, salt: str, log_repository: LogRepository) -> None:
        self._salt = salt
        self._log_repository = log_repository

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
            "para una investigación",
            "para fines educativos",
        }

    def _hash_value(self, value: str) -> str:
        """Hash PII with salt for anonymization."""
        return hashlib.sha256(f"{self._salt}:{value}".encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        # Lowercase + normalize unicode variants (e.g. ｂ → b, ﬁ → fi)
        normalized = unicodedata.normalize("NFKC", text.lower())
        # Replace punctuation and symbols with spaces (strips obfuscation like b@mb or b.o.m.b)
        normalized = re.sub(r"[\W_]+", " ", normalized)
        # Collapse multiple spaces into one and trim edges
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def evaluate(self, text: str) -> tuple[list[str], ModerationAction, str]:
        """Evaluate text for policy violations.

        Decision flow:
        1. Check for explicit risky keywords -> BLOCK immediately
        2. Check for jailbreak pattern (disguise + sensitive payload) -> FLAG
        3. If nothing detected -> ALLOW

        Returns:
            tuple: (detected_risks, action, reason)
        """
        normalized = self._normalize_text(text)
        risks: list[str] = []

        # Step 1: Scan for explicit risk keywords
        for risk, keywords in self._risk_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                risks.append(risk)

        if risks:
            return risks, ModerationAction.BLOCK, "Explicit risky content detected by keyword/pattern policy."

        # Step 2: Check for jailbreak attempts (requires BOTH conditions)
        if any(marker in normalized for marker in self._adversarial_context_markers) and any(
            token in normalized for token in ["credenciales", "password", "documento", "dni", "user id", "bypass"]
        ):
            return ["prompt_evasion"], ModerationAction.FLAG, "Potential adversarial framing detected for manual review."

        # Step 3: No risks detected
        return [], ModerationAction.ALLOW, "No risk detected under current policy."

    def build_log_record(
        self,
        user_id: str,
        text: str,
        detected_risks: list[str],
        action: ModerationAction,
        request_id: str,
    ) -> dict:
        """Build privacy-first log record with hashed PII."""
        retention_tag = "clean_30d"
        if action == ModerationAction.FLAG:
            retention_tag = "flagged_event_90d"
        elif action == ModerationAction.BLOCK:
            retention_tag = "incident_365d"

        return {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "request_id": request_id,
            "anonymized_user_id": self._hash_value(user_id),
            "input_hash": self._hash_value(text),
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
        """Build and persist log record via repository."""
        record = self.build_log_record(user_id, text, detected_risks, action, request_id)
        self._log_repository.write_log(record)
