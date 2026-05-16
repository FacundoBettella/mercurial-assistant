from src.domain.interfaces.pipeline_step import IPipelineStep
from src.application.pipeline.context import ProcessingState
from src.domain.services.moderation import ModerationService
from src.domain.entities.moderation_action import ModerationAction

class ModerationStep(IPipelineStep):
    """Evaluates content safety using ModerationService."""
    def __init__(self, moderation_service: ModerationService):
        self._moderation = moderation_service

    async def process(self, state: ProcessingState) -> ProcessingState:
        risks, action, reason = self._moderation.evaluate(
            state.request.text
        )

        from src.domain.entities.moderation_response import ModerationResponse
        state.moderation_result = ModerationResponse(
            flagged=(action != ModerationAction.ALLOW),
            detected_risks=risks,
            moderation_action=action,
            reason=reason
        )

        # Stop pipeline if blocked
        if action == ModerationAction.BLOCK:
            state.stop_pipeline(reason=f"Blocked: {reason}")

        return state
