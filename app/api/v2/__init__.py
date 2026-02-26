"""API v2 module."""

from app.api.v2.batch import router as batch_router
from app.api.v2.streaming import router as streaming_router

__all__ = ["batch_router", "streaming_router"]
