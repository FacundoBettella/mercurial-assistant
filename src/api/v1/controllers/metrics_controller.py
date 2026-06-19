from fastapi import APIRouter, Depends, Query
from src.api.v1.schemas import MetricSummaryResponseDTO
from src.domain.services.metric_summary_service import MetricSummaryService
from src.core.dependencies import get_metric_summary_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary", response_model=MetricSummaryResponseDTO)
def get_metrics_summary(
    model: str | None = Query(default=None, description="Filter by model name."),
    top_prompts: int = Query(default=5, ge=1, le=20, description="Number of top repeated prompts to return."),
    service: MetricSummaryService = Depends(get_metric_summary_service),
) -> MetricSummaryResponseDTO:
    return MetricSummaryResponseDTO(**service.summarize(model=model, top_prompts=top_prompts))
