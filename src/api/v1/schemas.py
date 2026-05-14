from pydantic import BaseModel, Field

class LLMGenerateRequestDTO(BaseModel):
    prompt: str = Field(min_length=1, description="Prompt to send to the LLM")
    model: str | None = Field(default=None, description="Optional model override")


class LLMGenerateResponseDTO(BaseModel):
    content: str = Field(description="Raw LLM completion")
