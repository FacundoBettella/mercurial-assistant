from abc import ABC, abstractmethod
from src.application.pipeline.context import ProcessingState


class IPipelineStep(ABC):
    """Interface for pipeline steps.

    Each step receives mutable state, processes it, and returns it.
    Steps work with domain entities inside the state.
    """

    @abstractmethod
    async def process(self, state: ProcessingState) -> ProcessingState:
        """Process the state and return modified state.

        Args:
            state: Current processing state with domain entities

        Returns:
            Modified state (same instance, mutated)
        """
        pass
