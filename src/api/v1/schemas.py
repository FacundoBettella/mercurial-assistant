from pydantic import BaseModel, Field

class LLMGenerateRequestDTO(BaseModel):
    prompt: str = Field(min_length=1, description="Prompt to send to the LLM")
    user_id: str = Field(min_length=1, description="User id")

class LLMGenerateResponseDTO(BaseModel):
    content: str = Field(description="Raw LLM completion")
