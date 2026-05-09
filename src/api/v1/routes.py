from fastapi import APIRouter
from src.api.v1 import llm_routes, moderation_routes

router = APIRouter(prefix="/api/v1")

router.include_router(llm_routes.router)
router.include_router(moderation_routes.router)

__all__ = ["router"]
