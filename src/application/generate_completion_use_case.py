from functools import lru_cache
from pathlib import Path

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.context import ProcessingState
from src.domain.entities.moderation_request import ModerationRequest
from src.domain.exceptions import ContentBlockedError


@lru_cache
def _load_system_prompt() -> str:
    """Load the fixed system prompt from the prompts folder."""
    project_root = Path(__file__).resolve().parents[2]
    prompt_path = project_root / "prompts" / "system_prompt.txt"
    return prompt_path.read_text(encoding="utf-8").strip()


class GenerateCompletionUseCase:
    """Orchestrates the full generation flow: moderation → LLM → logging."""

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    async def execute(self, prompt: str, model: str | None = None) -> str:
        state = ProcessingState(
            request=ModerationRequest(user_id="anonymous", text=prompt),
            system_prompt=_load_system_prompt(),
            model=model,
        )
        final_state = await self._pipeline.execute(state)

        if final_state.blocked:
            raise ContentBlockedError(final_state.error or "Content blocked by moderation")

        # llm_result is guaranteed to be set if pipeline ran LLMProcessingStep
        assert final_state.llm_result is not None
        return final_state.llm_result.content
