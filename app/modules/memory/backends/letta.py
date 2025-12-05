"""Letta AI memory backend using Learning SDK.

This backend uses Letta's Learning SDK for long-term memory management.
It provides sophisticated memory capabilities including semantic search
and background memory processing.

Maps KAI concepts to Letta:
- db_connection_id → agent name (each DB connection = separate Letta agent)
- namespace → memory block label
- key/value → stored in block value as structured content
"""

import json
import logging
from datetime import datetime
from typing import Any

from app.modules.memory.models import Memory, MemorySearchResult

logger = logging.getLogger(__name__)


class LettaMemoryBackend:
    """Memory backend using Letta AI Learning SDK.

    This backend provides:
    - Cloud-based memory storage via Letta
    - Semantic search capabilities
    - Agent-scoped memory isolation with hierarchical sharing
    - Background memory processing (sleeptime)

    Memory Hierarchy:
    - SHARED agent (kai_shared_{db}): Contains shared_knowledge block
      - shared_knowledge: Combined business_facts + data_insights (shared across all sessions)
    - SESSION agent (kai_agent_{db}_{session}): Contains session-specific blocks
      - user_preferences: Session-specific preferences
      - corrections: Session-specific corrections
      - general: Miscellaneous session data
    """

    # Shared memory block - stored in shared agent, visible to all sessions
    SHARED_MEMORY_BLOCK = "shared_knowledge"

    # Session-specific memory blocks
    SESSION_MEMORY_BLOCKS = [
        "user_preferences",
        "corrections",
        "general",
    ]

    # Legacy namespaces that map to shared_knowledge
    LEGACY_SHARED_NAMESPACES = ["business_facts", "data_insights"]

    # Default memory blocks for session agents
    DEFAULT_MEMORY_BLOCKS = SESSION_MEMORY_BLOCKS

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize Letta client.

        Args:
            api_key: Letta API key for authentication.
            base_url: Optional base URL for self-hosted Letta instances.
        """
        try:
            from letta_client import Letta
        except ImportError:
            raise ImportError(
                "Letta client not installed. Install with: pip install letta-client"
            )

        self.api_key = api_key
        self.base_url = base_url

        # Initialize Letta client
        if base_url:
            self.client = Letta(api_key=api_key, base_url=base_url)
        else:
            self.client = Letta(api_key=api_key)

        # Cache for agent existence checks
        self._agents_cache: dict[str, str] = {}  # agent_name -> agent_id

    def _get_agent_name(self, db_connection_id: str, is_shared: bool = False) -> str:
        """Convert db_connection_id to Letta agent name.

        Args:
            db_connection_id: The database connection identifier.
            is_shared: If True, returns shared agent name (for shared_knowledge).

        Returns:
            Agent name string.
        """
        # Sanitize name for Letta compatibility
        sanitized = db_connection_id.replace("-", "_").replace(" ", "_")
        if is_shared:
            return f"kai_shared_{sanitized}"
        return f"kai_memory_{sanitized}"

    def _is_shared_namespace(self, namespace: str) -> bool:
        """Check if namespace should be stored in shared agent.

        Args:
            namespace: The namespace to check.

        Returns:
            True if namespace is shared (shared_knowledge or legacy shared namespaces).
        """
        return (
            namespace == self.SHARED_MEMORY_BLOCK or
            namespace in self.LEGACY_SHARED_NAMESPACES
        )

    def _normalize_namespace(self, namespace: str) -> str:
        """Normalize legacy namespaces to shared_knowledge.

        Args:
            namespace: The namespace to normalize.

        Returns:
            Normalized namespace (shared_knowledge for legacy shared namespaces).
        """
        if namespace in self.LEGACY_SHARED_NAMESPACES:
            return self.SHARED_MEMORY_BLOCK
        return namespace

    def _ensure_agent(self, db_connection_id: str, is_shared: bool = False) -> str:
        """Ensure Letta agent exists for this connection.

        Args:
            db_connection_id: The database connection identifier.
            is_shared: If True, ensure shared agent exists.

        Returns:
            The agent ID.
        """
        agent_name = self._get_agent_name(db_connection_id, is_shared=is_shared)

        # Check cache first
        if agent_name in self._agents_cache:
            return self._agents_cache[agent_name]

        # Determine which memory blocks to create
        memory_blocks = (
            [self.SHARED_MEMORY_BLOCK] if is_shared else self.SESSION_MEMORY_BLOCKS
        )

        try:
            # List existing agents to find by name
            agents = self.client.agents.list()
            for agent in agents:
                if agent.name == agent_name:
                    self._agents_cache[agent_name] = agent.id
                    return agent.id

            # Agent doesn't exist, create it
            logger.info(f"Creating Letta agent: {agent_name} with blocks: {memory_blocks}")
            agent = self.client.agents.create(
                name=agent_name,
                memory_blocks=[
                    {"label": block, "value": ""}
                    for block in memory_blocks
                ],
            )
            self._agents_cache[agent_name] = agent.id
            return agent.id

        except Exception as e:
            logger.error(f"Failed to ensure Letta agent: {e}")
            raise

    def _format_memory_content(
        self, key: str, value: dict[str, Any], importance: float
    ) -> str:
        """Format memory key/value for storage in Letta block."""
        return json.dumps(
            {
                "key": key,
                "value": value,
                "importance": importance,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def _parse_block_content(
        self, db_connection_id: str, namespace: str, content: str
    ) -> list[Memory]:
        """Parse Letta block content into Memory objects."""
        memories = []
        if not content or not content.strip():
            return memories

        # Try to parse as JSON entries (newline-separated)
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                now = datetime.utcnow().isoformat()
                memory = Memory(
                    id=f"{namespace}:{data.get('key', 'unknown')}",
                    db_connection_id=db_connection_id,
                    namespace=namespace,
                    key=data.get("key", "unknown"),
                    value=data.get("value", {}),
                    content_text=str(data.get("value", "")),
                    importance=data.get("importance", 0.5),
                    access_count=0,
                    created_at=data.get("timestamp", now),
                    updated_at=now,
                )
                memories.append(memory)
            except json.JSONDecodeError:
                # Treat as plain text memory
                now = datetime.utcnow().isoformat()
                memory = Memory(
                    id=f"{namespace}:text_{hash(line)}",
                    db_connection_id=db_connection_id,
                    namespace=namespace,
                    key=f"text_{hash(line) % 10000}",
                    value={"content": line},
                    content_text=line,
                    importance=0.5,
                    access_count=0,
                    created_at=now,
                    updated_at=now,
                )
                memories.append(memory)

        return memories

    def remember(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        value: dict[str, Any],
        importance: float = 0.5,
        session_id: str | None = None,
    ) -> Memory:
        """Store a memory using Letta.

        The memory is appended to the appropriate memory block.
        Shared namespaces (business_facts, data_insights, shared_knowledge)
        are stored in the shared agent, accessible to all sessions.
        Session-specific namespaces are stored in the session agent.

        Args:
            db_connection_id: Database connection identifier.
            namespace: Memory namespace (will be normalized if legacy).
            key: Memory key.
            value: Memory value dictionary.
            importance: Importance score (0-1).
            session_id: Optional session ID (ignored for shared namespaces).

        Returns:
            The stored Memory object.
        """
        # Determine if this is a shared namespace
        is_shared = self._is_shared_namespace(namespace)
        # Normalize legacy namespaces to shared_knowledge
        effective_namespace = self._normalize_namespace(namespace)
        # Use shared or session agent
        agent_id = self._ensure_agent(db_connection_id, is_shared=is_shared)

        # Format memory content
        content = self._format_memory_content(key, value, importance)

        try:
            # Get existing block content
            blocks = self.client.agents.blocks.list(agent_id=agent_id)
            existing_content = ""
            block_id = None

            for block in blocks:
                if block.label == effective_namespace:
                    existing_content = block.value or ""
                    block_id = block.id
                    break

            # If block doesn't exist, create it at client level and attach to agent
            if block_id is None:
                logger.info(f"Creating memory block: {effective_namespace}")
                # Create block at client level
                block = self.client.blocks.create(
                    label=effective_namespace,
                    value=content,
                )
                # Attach to agent
                self.client.agents.blocks.attach(
                    agent_id=agent_id,
                    block_id=block.id,
                )
                block_id = block.id
            else:
                # Append new content to existing
                new_content = (
                    f"{existing_content}\n{content}"
                    if existing_content
                    else content
                )
                # Use block_label as positional arg for agents.blocks.update
                self.client.agents.blocks.update(
                    effective_namespace,  # block_label
                    agent_id=agent_id,
                    value=new_content,
                )

            now = datetime.utcnow().isoformat()
            return Memory(
                id=f"{effective_namespace}:{key}",
                db_connection_id=db_connection_id,
                namespace=effective_namespace,
                key=key,
                value=value,
                content_text=str(value),
                importance=importance,
                access_count=0,
                created_at=now,
                updated_at=now,
            )

        except Exception as e:
            logger.error(f"Failed to store memory in Letta: {e}")
            raise

    def recall(
        self,
        db_connection_id: str,
        query: str,
        namespace: str | None = None,
        limit: int = 5,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[MemorySearchResult]:
        """Search memories using text matching within memory blocks.

        This performs text-based search across memory blocks. Searches in both
        session agent and shared agent (if include_shared=True) to provide
        hierarchical memory access.

        Args:
            db_connection_id: Database connection identifier.
            query: Search query string.
            namespace: Optional namespace filter (will be normalized if legacy).
            limit: Maximum number of results.
            session_id: Optional session ID (not used directly, but for interface).
            include_shared: If True, also search shared agent's shared_knowledge.

        Returns:
            List of MemorySearchResult sorted by relevance score.
        """
        block_memories = []

        try:
            # Normalize namespace if provided
            effective_namespace = (
                self._normalize_namespace(namespace) if namespace else None
            )

            # If searching for a shared namespace, only search shared agent
            if namespace and self._is_shared_namespace(namespace):
                shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
                block_memories = self._search_in_blocks(
                    shared_agent_id, db_connection_id, query, effective_namespace, limit
                )
            else:
                # Search in session agent first
                session_agent_id = self._ensure_agent(db_connection_id, is_shared=False)
                block_memories = self._search_in_blocks(
                    session_agent_id, db_connection_id, query, effective_namespace, limit
                )

                # Also search in shared agent if include_shared is True
                if include_shared:
                    shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
                    shared_memories = self._search_in_blocks(
                        shared_agent_id,
                        db_connection_id,
                        query,
                        self.SHARED_MEMORY_BLOCK if not namespace else effective_namespace,
                        limit,
                    )
                    block_memories.extend(shared_memories)

            search_results = []
            for i, mem in enumerate(block_memories):
                # Calculate score based on match quality
                query_lower = query.lower()
                content_lower = mem.content_text.lower()

                # Better scoring: exact match vs partial
                if query_lower == content_lower:
                    score = 1.0
                elif query_lower in content_lower:
                    # Score based on how much of the content is the query
                    score = min(0.9, len(query) / max(len(mem.content_text), 1) + 0.5)
                else:
                    score = 0.5 - (i * 0.05)

                search_results.append(
                    MemorySearchResult(
                        memory=mem,
                        score=max(score, 0.1),
                        match_type="text",
                    )
                )

            # Sort by score and limit
            search_results.sort(key=lambda x: x.score, reverse=True)
            return search_results[:limit]

        except Exception as e:
            logger.warning(f"Letta search failed: {e}")
            return []

    def _search_in_blocks(
        self,
        agent_id: str,
        db_connection_id: str,
        query: str,
        namespace: str | None,
        limit: int,
    ) -> list[Memory]:
        """Search within memory blocks for matching content."""
        matching_memories = []
        query_lower = query.lower()

        try:
            blocks = self.client.agents.blocks.list(agent_id=agent_id)

            for block in blocks:
                if namespace and block.label != namespace:
                    continue

                memories = self._parse_block_content(
                    db_connection_id, block.label, block.value or ""
                )

                for memory in memories:
                    # Simple text matching
                    if query_lower in memory.content_text.lower():
                        matching_memories.append(memory)

            return matching_memories[:limit]

        except Exception as e:
            logger.warning(f"Block search failed: {e}")
            return []

    def get_memory(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> Memory | None:
        """Get a specific memory by namespace and key.

        Automatically routes to shared or session agent based on namespace.

        Args:
            db_connection_id: Database connection identifier.
            namespace: Memory namespace (will be normalized if legacy).
            key: Memory key.
            session_id: Optional session ID (for interface compatibility).

        Returns:
            Memory object if found, None otherwise.
        """
        # Determine which agent to use
        is_shared = self._is_shared_namespace(namespace)
        effective_namespace = self._normalize_namespace(namespace)
        agent_id = self._ensure_agent(db_connection_id, is_shared=is_shared)

        try:
            blocks = self.client.agents.blocks.list(agent_id=agent_id)

            for block in blocks:
                if block.label == effective_namespace:
                    memories = self._parse_block_content(
                        db_connection_id, effective_namespace, block.value or ""
                    )
                    for memory in memories:
                        if memory.key == key:
                            return memory

            return None

        except Exception as e:
            logger.warning(f"Failed to get memory: {e}")
            return None

    def forget(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> bool:
        """Delete a specific memory by removing it from the block.

        Automatically routes to shared or session agent based on namespace.

        Args:
            db_connection_id: Database connection identifier.
            namespace: Memory namespace (will be normalized if legacy).
            key: Memory key to delete.
            session_id: Optional session ID (for interface compatibility).

        Returns:
            True if memory was deleted, False otherwise.
        """
        # Determine which agent to use
        is_shared = self._is_shared_namespace(namespace)
        effective_namespace = self._normalize_namespace(namespace)
        agent_id = self._ensure_agent(db_connection_id, is_shared=is_shared)

        try:
            blocks = self.client.agents.blocks.list(agent_id=agent_id)

            for block in blocks:
                if block.label == effective_namespace:
                    # Parse existing content
                    memories = self._parse_block_content(
                        db_connection_id, effective_namespace, block.value or ""
                    )

                    # Filter out the memory to delete
                    remaining = [m for m in memories if m.key != key]

                    if len(remaining) < len(memories):
                        # Rebuild block content
                        new_content = "\n".join(
                            self._format_memory_content(m.key, m.value, m.importance)
                            for m in remaining
                        )
                        self.client.agents.blocks.update(
                            block.label,  # block_label as positional arg
                            agent_id=agent_id,
                            value=new_content,
                        )
                        return True

            return False

        except Exception as e:
            logger.warning(f"Failed to forget memory: {e}")
            return False

    def list_memories(
        self,
        db_connection_id: str,
        namespace: str | None = None,
        limit: int = 100,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[Memory]:
        """List memories, optionally filtered by namespace.

        Lists memories from both session agent and shared agent (if include_shared=True).

        Args:
            db_connection_id: Database connection identifier.
            namespace: Optional namespace filter (will be normalized if legacy).
            limit: Maximum number of results.
            session_id: Optional session ID (for interface compatibility).
            include_shared: If True, also list shared agent's shared_knowledge.

        Returns:
            List of Memory objects.
        """
        all_memories = []
        effective_namespace = (
            self._normalize_namespace(namespace) if namespace else None
        )

        try:
            # If listing a shared namespace specifically, only list from shared agent
            if namespace and self._is_shared_namespace(namespace):
                shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
                blocks = self.client.agents.blocks.list(agent_id=shared_agent_id)

                for block in blocks:
                    if effective_namespace and block.label != effective_namespace:
                        continue
                    memories = self._parse_block_content(
                        db_connection_id, block.label, block.value or ""
                    )
                    all_memories.extend(memories)
            else:
                # List from session agent
                session_agent_id = self._ensure_agent(db_connection_id, is_shared=False)
                blocks = self.client.agents.blocks.list(agent_id=session_agent_id)

                for block in blocks:
                    if effective_namespace and block.label != effective_namespace:
                        continue
                    memories = self._parse_block_content(
                        db_connection_id, block.label, block.value or ""
                    )
                    all_memories.extend(memories)

                # Also list from shared agent if include_shared is True
                if include_shared:
                    shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
                    shared_blocks = self.client.agents.blocks.list(agent_id=shared_agent_id)

                    for block in shared_blocks:
                        if effective_namespace and block.label != effective_namespace:
                            continue
                        memories = self._parse_block_content(
                            db_connection_id, block.label, block.value or ""
                        )
                        all_memories.extend(memories)

            return all_memories[:limit]

        except Exception as e:
            logger.warning(f"Failed to list memories: {e}")
            return []

    def list_namespaces(self, db_connection_id: str) -> list[str]:
        """List all namespaces (memory block labels) from both agents.

        Returns namespaces from both session agent and shared agent.

        Args:
            db_connection_id: Database connection identifier.

        Returns:
            List of namespace strings.
        """
        namespaces = set()

        try:
            # List from session agent
            session_agent_id = self._ensure_agent(db_connection_id, is_shared=False)
            session_blocks = self.client.agents.blocks.list(agent_id=session_agent_id)
            namespaces.update(block.label for block in session_blocks if block.label)

            # List from shared agent
            shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
            shared_blocks = self.client.agents.blocks.list(agent_id=shared_agent_id)
            namespaces.update(block.label for block in shared_blocks if block.label)

            return sorted(namespaces)

        except Exception as e:
            logger.warning(f"Failed to list namespaces: {e}")
            return []

    def clear_namespace(
        self,
        db_connection_id: str,
        namespace: str,
    ) -> int:
        """Clear all memories in a namespace.

        Automatically routes to shared or session agent based on namespace.

        Args:
            db_connection_id: Database connection identifier.
            namespace: Namespace to clear (will be normalized if legacy).

        Returns:
            Number of memories cleared.
        """
        # Determine which agent to use
        is_shared = self._is_shared_namespace(namespace)
        effective_namespace = self._normalize_namespace(namespace)
        agent_id = self._ensure_agent(db_connection_id, is_shared=is_shared)

        try:
            blocks = self.client.agents.blocks.list(agent_id=agent_id)

            for block in blocks:
                if block.label == effective_namespace:
                    # Count memories before clearing
                    memories = self._parse_block_content(
                        db_connection_id, effective_namespace, block.value or ""
                    )
                    count = len(memories)

                    # Clear the block
                    self.client.agents.blocks.update(
                        block.label,  # block_label as positional arg
                        agent_id=agent_id,
                        value="",
                    )
                    return count

            return 0

        except Exception as e:
            logger.warning(f"Failed to clear namespace: {e}")
            return 0

    def clear_all(self, db_connection_id: str) -> int:
        """Clear all memories for a database connection.

        Clears from both session agent and shared agent.

        Args:
            db_connection_id: Database connection identifier.

        Returns:
            Total number of memories cleared.
        """
        total_count = 0

        try:
            # Clear session agent
            session_agent_id = self._ensure_agent(db_connection_id, is_shared=False)
            session_blocks = self.client.agents.blocks.list(agent_id=session_agent_id)

            for block in session_blocks:
                memories = self._parse_block_content(
                    db_connection_id, block.label, block.value or ""
                )
                total_count += len(memories)

                self.client.agents.blocks.update(
                    block.label,
                    agent_id=session_agent_id,
                    value="",
                )

            # Clear shared agent
            shared_agent_id = self._ensure_agent(db_connection_id, is_shared=True)
            shared_blocks = self.client.agents.blocks.list(agent_id=shared_agent_id)

            for block in shared_blocks:
                memories = self._parse_block_content(
                    db_connection_id, block.label, block.value or ""
                )
                total_count += len(memories)

                self.client.agents.blocks.update(
                    block.label,
                    agent_id=shared_agent_id,
                    value="",
                )

            return total_count

        except Exception as e:
            logger.warning(f"Failed to clear all memories: {e}")
            return 0

    def format_memories_for_prompt(
        self,
        db_connection_id: str,
        query: str | None = None,
        namespace: str | None = None,
        limit: int = 10,
    ) -> str:
        """Format memories as a string for the agent prompt."""
        if query:
            results = self.recall(db_connection_id, query, namespace, limit)
            if not results:
                return "No relevant memories found."

            lines = ["# Relevant Memories\n"]
            for result in results:
                memory = result.memory
                lines.append(f"## [{memory.namespace}] {memory.key}")
                lines.append(f"**Relevance:** {result.score:.2f}")
                lines.append(f"**Content:** {memory.value}")
                lines.append("")
            return "\n".join(lines)

        else:
            memories = self.list_memories(db_connection_id, namespace, limit)
            if not memories:
                return "No memories stored."

            lines = ["# Stored Memories\n"]
            current_namespace = None
            for memory in sorted(memories, key=lambda m: (m.namespace, m.key)):
                if memory.namespace != current_namespace:
                    current_namespace = memory.namespace
                    lines.append(f"\n## {current_namespace}\n")
                lines.append(f"- **{memory.key}:** {memory.value}")

            return "\n".join(lines)
