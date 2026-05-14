"""Logging step for pipeline."""

from src.domain.interfaces.pipeline_step import IPipelineStep
from src.application.pipeline.context import ProcessingState
from src.domain.interfaces.log_repository import ILogRepository


class LoggingStep(IPipelineStep):
    """Logs the complete processing state.

    Depends on: ILogRepository
    Updates: nothing (read-only)
    Always executes: even if blocked
    """

    def __init__(self, log_repository: ILogRepository):
        self._log = log_repository

    async def process(self, state: ProcessingState) -> ProcessingState:
        """Log the complete state after processing."""
        log_data = {
            "user_id": state.request.user_id,
            "prompt": state.request.text,
            "moderation": {
                "action": state.moderation_result.moderation_action.value if state.moderation_result else None,
                "risks": state.moderation_result.detected_risks if state.moderation_result else [],
                "reason": state.moderation_result.reason if state.moderation_result else None
            },
            "llm": {
                "response": state.llm_result.content if state.llm_result else None,
                "model": state.llm_result.model_used if state.llm_result else None,
                "blocked": state.blocked
            },
            "error": state.error
        }

        self._log.write_log(log_data)

        return state
