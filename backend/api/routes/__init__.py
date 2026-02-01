"""
API Routes Module

FastAPI route handlers organized by domain.
"""

from .deals import router as deals_router
from .assets import router as assets_router
from .users import router as users_router
from .langgraph import router as langgraph_router

__all__ = [
    "deals_router",
    "assets_router",
    "users_router",
    "langgraph_router",
]
