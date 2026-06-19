from collections import Counter, defaultdict
from src.domain.interfaces.metric_repository import IMetricRepository


def _percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (p / 100) * (len(sorted_vals) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    return round(sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo]), 2)


class MetricSummaryService:
    def __init__(self, metric_repository: IMetricRepository) -> None:
        self._repo = metric_repository

    def summarize(self, model: str | None = None, top_prompts: int = 5) -> dict:
        rows = self._repo.read_all()

        if model:
            rows = [r for r in rows if r.get("model") == model]

        if not rows:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "avg_tokens_per_request": 0.0,
                "models_used": [],
                "by_model": {},
                "top_topics": [],
            }

        latencies = [float(r.get("latency_ms", 0)) for r in rows]
        total_tokens = sum(int(r.get("total_tokens", 0)) for r in rows)
        total_cost = sum(float(r.get("estimated_cost_usd", 0)) for r in rows)
        models = sorted({r["model"] for r in rows if r.get("model")})

        # Breakdown per model
        by_model: dict[str, dict] = defaultdict(lambda: {
            "requests": 0, "total_tokens": 0, "total_cost_usd": 0.0, "latencies": []
        })
        for r in rows:
            m = r.get("model", "unknown")
            by_model[m]["requests"] += 1
            by_model[m]["total_tokens"] += int(r.get("total_tokens", 0))
            by_model[m]["total_cost_usd"] += float(r.get("estimated_cost_usd", 0))
            by_model[m]["latencies"].append(float(r.get("latency_ms", 0)))

        by_model_summary = {
            m: {
                "requests": v["requests"],
                "total_tokens": v["total_tokens"],
                "total_cost_usd": round(v["total_cost_usd"], 6),
                "avg_latency_ms": round(sum(v["latencies"]) / len(v["latencies"]), 2),
            }
            for m, v in by_model.items()
        }

        # Top topics by frequency
        topic_counts = Counter(r["topic"] for r in rows if r.get("topic"))
        top = [{"topic": t, "count": c} for t, c in topic_counts.most_common(top_prompts)]

        return {
            "total_requests": len(rows),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "p50_latency_ms": _percentile(latencies, 50),
            "p95_latency_ms": _percentile(latencies, 95),
            "avg_tokens_per_request": round(total_tokens / len(rows), 1),
            "models_used": models,
            "by_model": by_model_summary,
            "top_topics": top,
        }
