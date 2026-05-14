from src.domain.interfaces.pipeline_step import IPipelineStep
from src.application.pipeline.context import ProcessingState

class Pipeline:
    """Pattern: Pipeline (Pipes and Filters)."""

    def __init__(self, steps: list[IPipelineStep]):
        self._steps = steps

    async def execute(self, state: ProcessingState) -> ProcessingState:
        """Execute all steps sequentially until completion or early stop.

        Args:
            state: Initial processing state

        Returns:
            Final state after all steps (or after early termination)
        """
        for step in self._steps:
            # Execute step
            state = await step.process(state)

            # Check if we should stop
            if not state.should_continue:
                break

        return state
