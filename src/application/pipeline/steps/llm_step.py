import json
import time
from src.domain.interfaces.pipeline_step import IPipelineStep
from src.application.pipeline.context import ProcessingState
from src.domain.interfaces.llm_provider import ILLMProvider
from src.domain.services.prompt_metric_service import PromptMetricService
from src.domain.entities.llm_response import LLMResponse
from src.core.config import settings

class LLMProcessingStep(IPipelineStep):
    def __init__(self, llm_provider: ILLMProvider, metric_service: PromptMetricService):
        self._llm = llm_provider
        self._metrics = metric_service

    async def process(self, state: ProcessingState) -> ProcessingState:
        if state.blocked:
            state.llm_result = LLMResponse.empty()
            return state

        start = time.perf_counter()
        result = await self._llm.generate(
            prompt=state.request.text,
            model=state.model,
            system_prompt=state.system_prompt,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        usage = result["usage"]
        tokens_prompt = usage["prompt_tokens"]
        tokens_completion = usage["completion_tokens"]
        total_tokens = usage["total_tokens"]

        model_key = state.model or "gpt-4o-mini"
        pricing = settings.MODEL_PRICING.get(model_key, settings.MODEL_PRICING["gpt-4o-mini"])
        estimated_cost_usd = (
            tokens_prompt * pricing["prompt"] +
            tokens_completion * pricing["completion"]
        )

        state.llm_result = LLMResponse(
            content=result["content"],
            model_used=state.model,
            tokens_used=total_tokens
        )

        try:
            topic = json.loads(result["content"]).get("topic", "unknown")
        except Exception:
            topic = "unknown"

        self._metrics.record(
            prompt=state.request.text,
            model=state.model,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=estimated_cost_usd,
            topic=topic,
        )

        return state
