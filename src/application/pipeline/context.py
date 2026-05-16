from dataclasses import dataclass
from src.domain.entities.moderation_request import ModerationRequest
from src.domain.entities.moderation_response import ModerationResponse
from src.domain.entities.llm_response import LLMResponse

@dataclass
class ProcessingState:
    """Mutable state to coordinate pipeline steps."""
    # Input (immutable domain entity)
    request: ModerationRequest
    # Runtime context forwarded by the use case
    system_prompt: str = ""
    model: str | None = None
    # Results from each step (domain entities)
    moderation_result: ModerationResponse | None = None
    llm_result: LLMResponse | None = None
    # Coordination flags (application concern)
    should_continue: bool = True
    blocked: bool = False
    error: str | None = None

    def stop_pipeline(self, reason: str = "blocked") -> None:
        self.should_continue = False
        self.blocked = True
        self.error = reason
