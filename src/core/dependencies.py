"""FastAPI dependency injection providers."""
from functools import lru_cache

from src.core.config import settings
from src.services.llm.factory import LLMProviderFactory
from src.services.llm.providers import LLMProvider


@lru_cache()
def get_llm_provider() -> LLMProvider:
    return LLMProviderFactory.create_provider(settings)
