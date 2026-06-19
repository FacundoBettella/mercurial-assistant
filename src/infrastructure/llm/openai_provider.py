import asyncio
import openai
from src.domain.interfaces.llm_provider import ILLMProvider
from src.domain.exceptions import LLMProviderError, LLMRateLimitError, LLMTimeoutError

_PROVIDER = "openai"
_MAX_RETRIES = 3
_BACKOFF_BASE = 2  # seconds — delay = base ^ attempt (2, 4, 8)


class OpenAIProvider(ILLMProvider):
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini") -> None:
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.default_model,
                    messages=messages,
                    max_tokens=200,
                    top_p=0.1,
                )
                usage = response.usage if hasattr(response, "usage") else None
                return {
                    "content": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0,
                    },
                }

            except openai.RateLimitError as e:
                last_exc = LLMRateLimitError(str(e), provider=_PROVIDER)
            except openai.APITimeoutError as e:
                last_exc = LLMTimeoutError(str(e), provider=_PROVIDER)
            except openai.APIError as e:
                raise LLMProviderError(str(e), provider=_PROVIDER) from e

            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_BACKOFF_BASE ** (attempt + 1))

        raise last_exc  # type: ignore[misc]
