import os
from functools import lru_cache
from src.core.config import settings
from src.domain.interfaces.llm_provider import ILLMProvider
from src.domain.interfaces.log_repository import ILogRepository
from src.infrastructure.llm.openai_provider import OpenAIProvider
from src.infrastructure.repositories.json_log import JsonLogRepository
from src.domain.services.moderation_service import ModerationEvaluator, ModerationService
from src.domain.services.prompt_metric_service import PromptMetricService
from src.infrastructure.repositories.metric_csv import CsvMetricRepository
from src.application.generate_completion_use_case import GenerateCompletionUseCase
from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.steps.moderation_step import ModerationStep
from src.application.pipeline.steps.llm_step import LLMProcessingStep
from src.application.pipeline.steps.logging_step import LoggingStep

@lru_cache
def get_llm_provider() -> ILLMProvider:
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        default_model=settings.openai_model
    )

@lru_cache
def get_log_repository() -> ILogRepository:
    logs_dir = os.getenv("LOGS_DIR")
    return JsonLogRepository(logs_dir=logs_dir)

@lru_cache
def get_moderation_evaluator() -> ModerationEvaluator:
    return ModerationEvaluator(salt=os.getenv("LOG_HASH_SALT"))

@lru_cache
def get_moderation_service() -> ModerationService:
    return ModerationService(evaluator=get_moderation_evaluator(), log_repository=get_log_repository())

@lru_cache
def get_metric_repository():
    metrics_dir = os.getenv("METRICS_DIR")
    os.makedirs(metrics_dir, exist_ok=True)
    metrics_path = os.path.join(metrics_dir, "metrics.csv")
    return CsvMetricRepository(csv_path=metrics_path)

@lru_cache
def get_prompt_metric_service():
    return PromptMetricService(metric_repository=get_metric_repository())

@lru_cache
def get_pipeline() -> Pipeline:
    """Steps are executed in order: Moderation → LLM → Logging."""
    return Pipeline(steps=[
        ModerationStep(get_moderation_service()),
        LLMProcessingStep(get_llm_provider(), get_prompt_metric_service()),
        LoggingStep(get_log_repository())
    ])

@lru_cache
def get_generate_completion_use_case() -> GenerateCompletionUseCase:
    return GenerateCompletionUseCase(pipeline=get_pipeline())
