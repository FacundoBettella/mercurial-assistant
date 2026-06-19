from unittest.mock import MagicMock
from src.domain.services.prompt_metric_service import PromptMetricService


@staticmethod
def make_service():
    return PromptMetricService(metric_repository=MagicMock())


def test_hash_is_case_insensitive():
    assert PromptMetricService._hash_prompt("Hola") == PromptMetricService._hash_prompt("hola")


def test_hash_ignores_extra_whitespace():
    assert PromptMetricService._hash_prompt("hola  mundo") == PromptMetricService._hash_prompt("hola mundo")


def test_hash_ignores_leading_trailing_whitespace():
    assert PromptMetricService._hash_prompt("  hola  ") == PromptMetricService._hash_prompt("hola")


def test_different_prompts_produce_different_hashes():
    assert PromptMetricService._hash_prompt("billing issue") != PromptMetricService._hash_prompt("technical issue")


def test_record_stores_topic_in_metric():
    repo = MagicMock()
    service = PromptMetricService(metric_repository=repo)

    service.record(
        prompt="me cobraron dos veces",
        model="gpt-4o-mini",
        tokens_prompt=100,
        tokens_completion=50,
        total_tokens=150,
        latency_ms=800.0,
        estimated_cost_usd=0.001,
        topic="billing",
    )

    written = repo.write_metric.call_args[0][0]
    assert written["topic"] == "billing"


def test_record_stores_prompt_hash_not_raw_text():
    repo = MagicMock()
    service = PromptMetricService(metric_repository=repo)

    service.record(
        prompt="texto sensible del usuario",
        model="gpt-4o-mini",
        tokens_prompt=10,
        tokens_completion=5,
        total_tokens=15,
        latency_ms=500.0,
        estimated_cost_usd=0.0001,
    )

    written = repo.write_metric.call_args[0][0]
    assert "prompt_hash" in written
    assert "texto sensible del usuario" not in written.values()


def test_record_defaults_topic_to_unknown():
    repo = MagicMock()
    service = PromptMetricService(metric_repository=repo)

    service.record(
        prompt="consulta",
        model="gpt-4o-mini",
        tokens_prompt=5,
        tokens_completion=5,
        total_tokens=10,
        latency_ms=300.0,
        estimated_cost_usd=0.0,
    )

    written = repo.write_metric.call_args[0][0]
    assert written["topic"] == "unknown"
