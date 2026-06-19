import json
from pathlib import Path
from functools import lru_cache

from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.context import ProcessingState
from src.domain.entities.moderation_request import ModerationRequest
from src.api.v1.schemas import LLMGenerateResponseDTO
from src.domain.exceptions import ContentBlockedError, LLMResponseParseError
from src.core.config import settings

@lru_cache
def _load_main_prompt() -> str:
    project_root = Path(__file__).resolve().parents[2]
    prompt_path = project_root / "prompts" / "main_prompt.txt"
    return prompt_path.read_text(encoding="utf-8").strip()

class GenerateCompletionUseCase:
    """Handle the full generation flow: moderation → LLM → metric → logging."""
    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    async def execute(self, prompt: str) -> LLMGenerateResponseDTO:
        state = ProcessingState(
            request=ModerationRequest(user_id="anonymous", text=prompt),
            system_prompt=_load_main_prompt(),
            model=settings.openai_model  # Siempre setea un modelo válido
        )
        final_state = await self._pipeline.execute(state)

        if final_state.blocked:
            raise ContentBlockedError(final_state.error or "Content blocked by moderation")

        assert final_state.llm_result is not None
        raw = final_state.llm_result.content
        try:
            parsed = json.loads(raw)
            return LLMGenerateResponseDTO(
                answer=parsed["answer"],
                confidence=parsed["confidence"],
                actions=parsed["actions"],
                priority=parsed["priority"],
                churn_risk=parsed["churn_risk"],
            )
        except Exception as e:
            raise LLMResponseParseError(raw=raw, cause=e) from e
