from openai import AsyncOpenAI
from src.domain.interfaces.llm_provider import ILLMProvider


class OpenAIProvider(ILLMProvider):
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini") -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        messages = []
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            instructions=system_prompt,
            messages=messages,
            max_output_tokens=150,
        )
        return response.choices[0].message.content
