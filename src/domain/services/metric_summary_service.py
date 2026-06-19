from src.domain.interfaces.metric_repository import IMetricRepository


class MetricSummaryService:
    def __init__(self, metric_repository: IMetricRepository) -> None:
        self._repo = metric_repository

    def summarize(self) -> dict:
        rows = self._repo.read_all()
        if not rows:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "avg_tokens_per_request": 0.0,
                "models_used": [],
            }

        total_tokens = sum(int(r.get("total_tokens", 0)) for r in rows)
        total_cost = sum(float(r.get("estimated_cost_usd", 0)) for r in rows)
        avg_latency = sum(float(r.get("latency_ms", 0)) for r in rows) / len(rows)
        models = sorted({r["model"] for r in rows if r.get("model")})

        return {
            "total_requests": len(rows),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_tokens_per_request": round(total_tokens / len(rows), 1),
            "models_used": models,
        }
