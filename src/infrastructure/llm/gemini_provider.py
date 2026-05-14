"""Google Gemini provider implementation."""
from src.domain.interfaces.llm_provider import ILLMProvider


class GeminiProvider(ILLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str, default_model: str = "gemini-1.5-pro") -> None:
        self.api_key = api_key
        self.default_model = default_model
        # import google.generativeai as genai
        # genai.configure(api_key=self.api_key)
        # self.client = genai.GenerativeModel(self.default_model)

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Generate completion from Gemini."""
        _ = (prompt, model, system_prompt)
        raise NotImplementedError("Gemini provider not yet implemented")
