from fastapi import APIRouter, Depends
from src.api.v1.schemas import LLMGenerateRequestDTO, LLMGenerateResponseDTO
from src.application.generate_completion_use_case import GenerateCompletionUseCase
from src.core.dependencies import get_generate_completion_use_case

router = APIRouter(prefix="/llm", tags=["LLM"])

@router.post("/generate", response_model=LLMGenerateResponseDTO)
async def generate_completion(
    body: LLMGenerateRequestDTO,
    use_case: GenerateCompletionUseCase = Depends(get_generate_completion_use_case),
) -> LLMGenerateResponseDTO:
    result = await use_case.execute(
        prompt=body.prompt,
        model=body.model,
    )
    return LLMGenerateResponseDTO(content=result)
