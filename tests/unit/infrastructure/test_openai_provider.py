import pytest
import openai
from unittest.mock import AsyncMock, MagicMock, patch
from src.infrastructure.llm.openai_provider import OpenAIProvider, _MAX_RETRIES
from src.domain.exceptions import LLMProviderError, LLMRateLimitError, LLMTimeoutError


def make_openai_response(content: str = "respuesta", prompt_tokens: int = 10, completion_tokens: int = 20):
    usage = MagicMock(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    response.usage = usage
    return response


def make_rate_limit_error() -> openai.RateLimitError:
    return openai.RateLimitError("rate limited", response=MagicMock(), body={})


def make_timeout_error() -> openai.APITimeoutError:
    return openai.APITimeoutError(request=MagicMock())


def make_api_error() -> openai.APIError:
    return openai.APIError("server error", request=MagicMock(), body={})


@pytest.fixture
def provider() -> OpenAIProvider:
    return OpenAIProvider(api_key="test-key", default_model="gpt-4o-mini")


async def test_returns_content_and_usage_on_success(provider):
    mock_create = AsyncMock(return_value=make_openai_response("hola", 5, 15))
    with patch.object(provider.client.chat.completions, "create", mock_create):
        result = await provider.generate(prompt="test", model="gpt-4o-mini")

    assert result["content"] == "hola"
    assert result["usage"]["prompt_tokens"] == 5
    assert result["usage"]["total_tokens"] == 20


async def test_retries_on_rate_limit_and_succeeds(provider):
    mock_create = AsyncMock(side_effect=[make_rate_limit_error(), make_openai_response("ok")])
    with patch.object(provider.client.chat.completions, "create", mock_create):
        with patch("src.infrastructure.llm.openai_provider.asyncio.sleep", AsyncMock()):
            result = await provider.generate(prompt="test", model="gpt-4o-mini")

    assert result["content"] == "ok"
    assert mock_create.call_count == 2


async def test_raises_rate_limit_error_after_exhausting_retries(provider):
    mock_create = AsyncMock(side_effect=make_rate_limit_error())
    with patch.object(provider.client.chat.completions, "create", mock_create):
        with patch("src.infrastructure.llm.openai_provider.asyncio.sleep", AsyncMock()):
            with pytest.raises(LLMRateLimitError):
                await provider.generate(prompt="test", model="gpt-4o-mini")

    assert mock_create.call_count == _MAX_RETRIES


async def test_retries_on_timeout_and_raises_after_exhausting(provider):
    mock_create = AsyncMock(side_effect=make_timeout_error())
    with patch.object(provider.client.chat.completions, "create", mock_create):
        with patch("src.infrastructure.llm.openai_provider.asyncio.sleep", AsyncMock()):
            with pytest.raises(LLMTimeoutError):
                await provider.generate(prompt="test", model="gpt-4o-mini")

    assert mock_create.call_count == _MAX_RETRIES


async def test_raises_provider_error_immediately_on_api_error(provider):
    mock_create = AsyncMock(side_effect=make_api_error())
    with patch.object(provider.client.chat.completions, "create", mock_create):
        with pytest.raises(LLMProviderError):
            await provider.generate(prompt="test", model="gpt-4o-mini")

    assert mock_create.call_count == 1  # no retry
