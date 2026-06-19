from fastapi import APIRouter
from .controllers.llm_controller import router as llm_router
from .controllers.metrics_controller import router as metrics_router

router = APIRouter(prefix="/api/v1")
router.include_router(llm_router)
router.include_router(metrics_router)

__all__ = ["router"]
