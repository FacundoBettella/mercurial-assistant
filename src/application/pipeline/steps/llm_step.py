from src.domain.interfaces.pipeline_step import IPipelineStep
from src.application.pipeline.context import ProcessingState
from src.domain.interfaces.llm_provider import ILLMProvider
from src.domain.entities.llm_response import LLMResponse

class LLMProcessingStep(IPipelineStep):
    """Processes prompt with LLM if moderation allows it.

    Depends on: ILLMProvider
    Updates: state.llm_result
    Skips if: state.blocked is True
    """

    def __init__(self, llm_provider: ILLMProvider):
        self._llm = llm_provider

    async def process(self, state: ProcessingState) -> ProcessingState:
        if state.blocked:
            state.llm_result = LLMResponse.empty()
            return state

        response_text = await self._llm.generate(
            prompt=state.request.text,
            model=state.model,
            system_prompt=state.system_prompt or None,
        )

        state.llm_result = LLMResponse(
            content=response_text,
            model_used=state.model or "default",
            tokens_used=0,
        )

        return state
