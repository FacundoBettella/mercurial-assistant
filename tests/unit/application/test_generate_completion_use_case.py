import json
import pytest
from unittest.mock import AsyncMock
from src.application.generate_completion_use_case import GenerateCompletionUseCase
from src.domain.entities.llm_response import LLMResponse
from src.domain.exceptions import ContentBlockedError, LLMResponseParseError

VALID_RESPONSE = json.dumps({
    "answer": "Hola, te ayudamos enseguida.",
    "confidence": 0.9,
    "actions": ["Encolar ticket como alto"],
    "priority": "high",
    "churn_risk": 0.6,
    "topic": "billing",
})


def make_pipeline(*, blocked: bool = False, content: str = VALID_RESPONSE) -> AsyncMock:
    pipeline = AsyncMock()

    async def execute(state):
        if blocked:
            state.stop_pipeline("blocked by moderation")
        else:
            state.llm_result = LLMResponse(content=content, model_used="gpt-4o-mini")
        return state

    pipeline.execute.side_effect = execute
    return pipeline


async def test_returns_dto_on_valid_llm_response():
    use_case = GenerateCompletionUseCase(pipeline=make_pipeline())
    result = await use_case.execute("me cobraron dos veces")
    assert result.priority == "high"
    assert result.confidence == 0.9
    assert result.churn_risk == 0.6
    assert result.topic == "billing"


async def test_topic_defaults_to_unknown_when_missing():
    no_topic = json.dumps({
        "answer": "ok", "confidence": 0.8, "actions": [], "priority": "low", "churn_risk": 0.1
    })
    use_case = GenerateCompletionUseCase(pipeline=make_pipeline(content=no_topic))
    result = await use_case.execute("consulta general")
    assert result.topic == "unknown"


async def test_raises_content_blocked_error_when_pipeline_blocks():
    use_case = GenerateCompletionUseCase(pipeline=make_pipeline(blocked=True))
    with pytest.raises(ContentBlockedError):
        await use_case.execute("texto con contenido bloqueado")


async def test_raises_parse_error_on_malformed_json():
    use_case = GenerateCompletionUseCase(pipeline=make_pipeline(content="esto no es json {{"))
    with pytest.raises(LLMResponseParseError) as exc_info:
        await use_case.execute("pregunta normal")
    assert "esto no es json" in exc_info.value.raw


async def test_raises_parse_error_on_missing_field():
    incomplete = json.dumps({"answer": "ok"})  # missing confidence, actions, etc.
    use_case = GenerateCompletionUseCase(pipeline=make_pipeline(content=incomplete))
    with pytest.raises(LLMResponseParseError):
        await use_case.execute("pregunta normal")
