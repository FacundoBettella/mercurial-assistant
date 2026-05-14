"""Dependency injection container."""
import os
from functools import lru_cache
from src.core.config import settings
from src.domain.interfaces.llm_provider import ILLMProvider
from src.domain.interfaces.log_repository import ILogRepository
from src.infrastructure.llm.openai_provider import OpenAIProvider
from src.infrastructure.repositories.json_log import JsonLogRepository
from src.application.moderation_service import ModerationService
from src.application.generate_completion_use_case import GenerateCompletionUseCase
from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.steps.moderation_step import ModerationStep
from src.application.pipeline.steps.llm_step import LLMProcessingStep
from src.application.pipeline.steps.logging_step import LoggingStep

@lru_cache
def get_llm_provider() -> ILLMProvider:
    """Factory function for LLM provider with dependency injection."""
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        default_model=settings.openai_model
    )


@lru_cache
def get_log_repository() -> ILogRepository:
    """Factory function for log repository."""
    logs_dir = os.getenv("LOGS_DIR", "logs")
    return JsonLogRepository(logs_dir=logs_dir)


@lru_cache
def get_moderation_service() -> ModerationService:
    """Factory function for moderation service."""
    salt = os.getenv("LOG_HASH_SALT", "dev-salt")
    log_repo = get_log_repository()
    return ModerationService(salt=salt, log_repository=log_repo)


@lru_cache
def get_generate_completion_use_case() -> GenerateCompletionUseCase:
    """Factory function for the LLM completion use case."""
    return GenerateCompletionUseCase(pipeline=get_pipeline())


@lru_cache
def get_pipeline() -> Pipeline:
    """Factory function for processing pipeline.

    Pipeline pattern: Sequential steps with early termination.
    Steps are executed in order: Moderation → LLM → Logging
    """
    return Pipeline(steps=[
        ModerationStep(get_moderation_service()),
        LLMProcessingStep(get_llm_provider()),
        LoggingStep(get_log_repository())
    ])
