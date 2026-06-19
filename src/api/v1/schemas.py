from pydantic import BaseModel, Field


class LLMGenerateRequestDTO(BaseModel):
    prompt: str = Field(min_length=1, description="User's question or instruction.")


class MetricSummaryResponseDTO(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    avg_tokens_per_request: float
    models_used: list[str]

class LLMGenerateResponseDTO(BaseModel):
    answer: str = Field(..., description="Model-generated answer, ready to display to the end user.")
    confidence: float = Field(..., ge=0, le=1, description="Estimated confidence (0 to 1) in the generated answer.")
    actions: list[str] = Field(..., description="Recommended actions for the agent or downstream system.")
    priority: str = Field(..., description="Ticket priority: low, medium, high, or critical.")
    churn_risk: float = Field(..., ge=0, le=1, description="Estimated risk of customer churn (0 to 1).")
