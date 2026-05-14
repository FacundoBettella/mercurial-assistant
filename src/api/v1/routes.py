from fastapi import APIRouter
from .controllers.llm_controller import router as llm_router

router = APIRouter(prefix="/api/v1")
router.include_router(llm_router)

__all__ = ["router"]
