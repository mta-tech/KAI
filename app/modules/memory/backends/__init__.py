"""Memory backend factory and exports.

This module provides the factory function for creating memory backends
and exports the backend protocol for type hints.
"""

import logging
import os
from typing import TYPE_CHECKING

from app.modules.memory.backends.base import MemoryBackend

if TYPE_CHECKING:
    from app.data.db.storage import Storage

logger = logging.getLogger(__name__)


def create_memory_backend(
    storage: "Storage" = None,
    backend_type: str | None = None,
) -> MemoryBackend:
    """Create appropriate memory backend based on configuration.

    The factory automatically selects the backend based on:
    1. Explicit backend_type parameter
    2. MEMORY_BACKEND setting from config
    3. Availability of LETTA_API_KEY

    Args:
        storage: TypeSense storage instance (required for typesense backend).
        backend_type: Override backend type ("typesense" or "letta").

    Returns:
        Configured memory backend implementing MemoryBackend protocol.

    Raises:
        ValueError: If Letta backend requested but API key not configured.
        ImportError: If Letta client not installed when Letta backend requested.
    """
    from app.server.config import get_settings

    settings = get_settings()
    backend = backend_type or settings.MEMORY_BACKEND

    # Check for Letta API key
    letta_api_key = settings.LETTA_API_KEY or os.getenv("LETTA_API_KEY")

    if backend == "letta":
        if not letta_api_key:
            logger.warning(
                "Letta backend requested but LETTA_API_KEY not set. "
                "Falling back to TypeSense."
            )
            backend = "typesense"
        else:
            try:
                from app.modules.memory.backends.letta import LettaMemoryBackend

                logger.info("Using Letta memory backend")
                return LettaMemoryBackend(
                    api_key=letta_api_key,
                    base_url=settings.LETTA_BASE_URL,
                )
            except ImportError as e:
                logger.warning(
                    f"Letta client not installed ({e}). Falling back to TypeSense. "
                    "Install with: pip install letta-client"
                )
                backend = "typesense"

    # Default to TypeSense
    from app.modules.memory.backends.typesense import TypeSenseMemoryBackend

    if storage is None:
        from app.data.db.storage import Storage

        storage = Storage(settings)

    logger.info("Using TypeSense memory backend")
    return TypeSenseMemoryBackend(storage)


__all__ = [
    "MemoryBackend",
    "create_memory_backend",
]
