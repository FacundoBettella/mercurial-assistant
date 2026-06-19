import hashlib
from datetime import datetime, timezone
from src.domain.interfaces.metric_repository import IMetricRepository


class PromptMetricService:
    """Business logic for formatting and recording prompt metrics."""

    def __init__(self, metric_repository: IMetricRepository) -> None:
        self._repo = metric_repository

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
        timestamp: str | None = None,
    ) -> None:
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        metric = {
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "prompt_hash": prompt_hash,
            "model": model,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "estimated_cost_usd": estimated_cost_usd,
        }
        self._repo.write_metric(metric)
