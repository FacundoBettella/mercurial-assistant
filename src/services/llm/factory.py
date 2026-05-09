from src.core.config import Settings, LLMProviderType
from src.services.llm.providers import LLMProvider, OpenAIProvider, GeminiProvider


class LLMProviderFactory:
    """Factory to create the appropriate LLM provider based on configuration."""

    @staticmethod
    def create_provider(settings: Settings) -> LLMProvider:
        """
        Create and return the configured LLM provider.

        Args:
            settings: Application settings containing provider configuration

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is unsupported or API key is missing
        """
        match settings.llm_provider:
            case LLMProviderType.OPENAI:
                if not settings.openai_api_key:
                    raise ValueError("OPENAI_API_KEY not configured")
                return OpenAIProvider(
                    api_key=settings.openai_api_key,
                    default_model=settings.openai_model
                )

            case LLMProviderType.GEMINI:
                if not settings.gemini_api_key:
                    raise ValueError("GEMINI_API_KEY not configured")
                return GeminiProvider(
                    api_key=settings.gemini_api_key,
                    default_model=settings.gemini_model
                )

            case _:
                raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
