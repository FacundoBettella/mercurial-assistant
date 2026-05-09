from fastapi import APIRouter, Depends
from src.core.dependencies import get_llm_provider

router = APIRouter(prefix="/llm", tags=["LLM"])

@router.post("/generate")
async def generate_completion(prompt: str, llm = Depends(get_llm_provider)):
    result = await llm.generate(prompt)
    return {result:"result "}
