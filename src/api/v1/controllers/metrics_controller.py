from fastapi import APIRouter, Depends
from src.api.v1.schemas import MetricSummaryResponseDTO
from src.domain.services.metric_summary_service import MetricSummaryService
from src.core.dependencies import get_metric_summary_service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary", response_model=MetricSummaryResponseDTO)
def get_metrics_summary(
    service: MetricSummaryService = Depends(get_metric_summary_service),
) -> MetricSummaryResponseDTO:
    return MetricSummaryResponseDTO(**service.summarize())
