from abc import ABC, abstractmethod
from openai import AsyncOpenAI


class LLMProvider(ABC):
    """Abstract base class for AI Provider."""

    @abstractmethod
    async def generate(self, prompt: str, model: str) -> str:
        """Generate completion from LLM."""
        pass



class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini") -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate completion from OpenAI."""
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=100
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str, default_model: str = "gemini-1.5-pro") -> None:
        self.api_key = api_key
        self.default_model = default_model
        # import google.generativeai as genai
        # genai.configure(api_key=self.api_key)
        # self.client = genai.GenerativeModel(self.default_model)

    async def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate completion from Gemini."""
        raise NotImplementedError("Gemini provider not yet implemented")







