"""Typesense-backed checkpointer for LangGraph session persistence."""
import json
import time
from typing import Any, AsyncIterator, Optional, Sequence, Tuple

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langchain_core.runnables import RunnableConfig

from app.modules.session.constants import SESSION_COLLECTION_NAME


class TypesenseCheckpointer(BaseCheckpointSaver):
    """
    Custom LangGraph checkpointer that persists to Typesense.

    This enables session state to be saved and restored across
    multiple queries, allowing for resumable conversations.
    """

    def __init__(self, storage: Any):
        """
        Initialize checkpointer with Typesense storage.

        Args:
            storage: Typesense storage instance
        """
        super().__init__()
        self.storage = storage
        self.collection = SESSION_COLLECTION_NAME

    def _get_thread_id(self, config: RunnableConfig) -> str:
        """Extract thread_id (session_id) from config."""
        return config["configurable"]["thread_id"]

    def _serialize(self, checkpoint: Checkpoint) -> str:
        """Serialize checkpoint to JSON string."""
        return json.dumps(checkpoint, default=str)

    def _deserialize(self, data: str) -> Checkpoint:
        """Deserialize checkpoint from JSON string."""
        return json.loads(data)

    async def aget(self, config: RunnableConfig) -> Optional[Checkpoint]:
        """
        Get the latest checkpoint for a session.

        Args:
            config: Runnable config containing thread_id

        Returns:
            Checkpoint if exists, None otherwise
        """
        thread_id = self._get_thread_id(config)
        # Storage methods are synchronous
        doc = self.storage.find_by_id(self.collection, thread_id)

        if doc and doc.get("checkpoint"):
            return self._deserialize(doc["checkpoint"])
        return None

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Get checkpoint tuple with metadata.

        Args:
            config: Runnable config containing thread_id

        Returns:
            CheckpointTuple if exists, None otherwise
        """
        thread_id = self._get_thread_id(config)
        # Storage methods are synchronous
        doc = self.storage.find_by_id(self.collection, thread_id)

        if doc and doc.get("checkpoint"):
            checkpoint = self._deserialize(doc["checkpoint"])
            metadata = doc.get("checkpoint_metadata", {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None
            )
        return None

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """
        List checkpoints (single checkpoint per session in this implementation).

        Args:
            config: Runnable config containing thread_id
            filter: Optional filter criteria
            before: Optional config to get checkpoints before
            limit: Maximum number of checkpoints to return

        Yields:
            CheckpointTuple for each matching checkpoint
        """
        if config:
            tuple_result = await self.aget_tuple(config)
            if tuple_result:
                yield tuple_result

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any]
    ) -> RunnableConfig:
        """
        Save checkpoint to Typesense.

        Args:
            config: Runnable config containing thread_id
            checkpoint: Checkpoint data to save
            metadata: Checkpoint metadata
            new_versions: New channel versions

        Returns:
            Updated config with checkpoint ID
        """
        thread_id = self._get_thread_id(config)

        # Storage methods are synchronous
        self.storage.update_or_create(
            self.collection,
            {"id": thread_id},
            {
                "checkpoint": self._serialize(checkpoint),
                "checkpoint_metadata": json.dumps(metadata) if metadata else "{}",
                "updated_at": int(time.time())
            }
        )

        return {
            **config,
            "configurable": {
                **config.get("configurable", {}),
                "checkpoint_id": checkpoint.get("id", thread_id)
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str
    ) -> None:
        """
        Save intermediate writes (not implemented for Typesense).

        For simplicity, this implementation only saves full checkpoints.
        """
        pass

    # Sync methods (delegate to async)
    def get(self, config: RunnableConfig) -> Optional[Checkpoint]:
        """Sync version of aget - not recommended for production."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.aget(config))

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Sync version of aget_tuple - not recommended for production."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.aget_tuple(config))

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any]
    ) -> RunnableConfig:
        """Sync version of aput - not recommended for production."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            self.aput(config, checkpoint, metadata, new_versions)
        )

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str
    ) -> None:
        """Sync version of aput_writes."""
        pass


__all__ = ["TypesenseCheckpointer"]
