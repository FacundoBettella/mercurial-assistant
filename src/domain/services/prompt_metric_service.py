import hashlib
import re
from datetime import datetime, timezone
from src.domain.interfaces.metric_repository import IMetricRepository


class PromptMetricService:
    """Business logic for formatting and recording prompt metrics."""

    def __init__(self, metric_repository: IMetricRepository) -> None:
        self._repo = metric_repository

    @staticmethod
    def _hash_prompt(prompt: str) -> str:
        normalized = re.sub(r"\s+", " ", prompt.lower().strip())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def record(
        self,
        *,
        prompt: str,
        model: str,
        tokens_prompt: int,
        tokens_completion: int,
        total_tokens: int,
        latency_ms: float,
        estimated_cost_usd: float,
        topic: str = "unknown",
        timestamp: str | None = None,
    ) -> None:
        metric = {
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "prompt_hash": self._hash_prompt(prompt),
            "topic": topic,
            "model": model,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "estimated_cost_usd": estimated_cost_usd,
        }
        self._repo.write_metric(metric)
