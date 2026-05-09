"""API v1 routes."""
from src.api.v1 import llm_routes, moderation_routes
from src.api.v1.routes import router

__all__ = ["router", "llm_routes", "moderation_routes"]
