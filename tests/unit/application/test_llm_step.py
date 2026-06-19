import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.application.pipeline.steps.llm_step import LLMProcessingStep
from src.application.pipeline.context import ProcessingState
from src.domain.entities.moderation_request import ModerationRequest


def make_state(text: str = "test ticket") -> ProcessingState:
    return ProcessingState(
        request=ModerationRequest(user_id="u1", text=text),
        system_prompt="sys",
        model="gpt-4o-mini",
    )


def make_llm_response(content: str) -> dict:
    return {
        "content": content,
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


def make_step(content: str):
    llm = AsyncMock()
    llm.generate.return_value = make_llm_response(content)
    metrics = MagicMock()
    return LLMProcessingStep(llm_provider=llm, metric_service=metrics), metrics


async def test_extracts_topic_from_llm_json():
    payload = json.dumps({"answer": "ok", "topic": "billing"})
    step, metrics = make_step(payload)

    await step.process(make_state())

    _, kwargs = metrics.record.call_args
    assert kwargs["topic"] == "billing"


async def test_topic_defaults_to_unknown_when_field_missing():
    payload = json.dumps({"answer": "ok"})
    step, metrics = make_step(payload)

    await step.process(make_state())

    _, kwargs = metrics.record.call_args
    assert kwargs["topic"] == "unknown"


async def test_topic_defaults_to_unknown_on_malformed_json():
    step, metrics = make_step("this is not json {{")

    await step.process(make_state())

    _, kwargs = metrics.record.call_args
    assert kwargs["topic"] == "unknown"


async def test_skips_llm_call_when_blocked():
    llm = AsyncMock()
    metrics = MagicMock()
    step = LLMProcessingStep(llm_provider=llm, metric_service=metrics)

    state = make_state()
    state.stop_pipeline("blocked")
    await step.process(state)

    llm.generate.assert_not_called()
    metrics.record.assert_not_called()
