"""Context Platform API.

This module exports the context platform endpoints for integration
with the main API class.
"""

from app.modules.context_platform.api.endpoints import (
    ContextPlatformEndpoints,
)

__all__ = [
    "ContextPlatformEndpoints",
]
