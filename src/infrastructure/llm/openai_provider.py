from openai import AsyncOpenAI
from src.domain.interfaces.llm_provider import ILLMProvider

class OpenAIProvider(ILLMProvider):
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini") -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=50,
            top_p=0.1
        )
        return response.choices[0].message.content
