"""Memory tools for autonomous agent long-term memory."""

import json
import logging
from datetime import datetime

from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection
from app.modules.memory.services import MemoryService

logger = logging.getLogger(__name__)


def _calculate_age(created_at: str) -> str:
    """Calculate human-readable age of a memory."""
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now()
        if created.tzinfo:
            now = datetime.now(created.tzinfo)
        delta = now - created

        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year(s) ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month(s) ago"
        elif delta.days > 0:
            return f"{delta.days} day(s) ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour(s) ago"
        else:
            return "recently"
    except Exception:
        return "unknown"


def _is_potentially_stale(created_at: str, namespace: str) -> bool:
    """Check if a memory might be stale based on age and type."""
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now()
        if created.tzinfo:
            now = datetime.now(created.tzinfo)
        delta = now - created

        # Different staleness thresholds by namespace
        if namespace == "shared_knowledge":
            return delta.days > 60  # Shared business/data knowledge - moderate threshold
        elif namespace in ("data_insights", "business_facts"):
            # Legacy namespace support
            return delta.days > 60
        elif namespace == "user_preferences":
            return delta.days > 180  # Preferences are more stable
        elif namespace == "corrections":
            return delta.days > 90  # Corrections remain valid longer
        else:
            return delta.days > 60
    except Exception:
        return False


def create_remember_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool for storing memories."""
    service = MemoryService(storage)

    def remember(
        namespace: str,
        key: str,
        content: str,
        importance: float = 0.5,
    ) -> str:
        """Store important information for future reference across conversations.

        Use this to remember:
        - User preferences (e.g., preferred date formats, reporting styles)
        - Business facts and data insights (shared across all sessions)
        - Corrections or clarifications from the user

        Memory persists across conversations and can be recalled later.

        Args:
            namespace: Category of memory. Use one of:
                - "shared_knowledge": Business facts + data insights (SHARED across sessions)
                - "user_preferences": User's preferred formats, styles, defaults
                - "corrections": User corrections to your understanding
                - "general": Miscellaneous session-specific information
            key: Unique identifier for this memory (e.g., "date_format_preference")
            content: The information to remember
            importance: How important this memory is (0-1, default 0.5)
                - 1.0: Critical - always recall
                - 0.7: High - recall for related queries
                - 0.5: Normal - recall when relevant
                - 0.3: Low - background information

        Returns:
            JSON string confirming the memory was stored.
        """
        try:
            memory = service.remember(
                db_connection_id=db_connection.id,
                namespace=namespace,
                key=key,
                value={"content": content},
                importance=importance,
            )

            return json.dumps({
                "success": True,
                "action": "remembered",
                "namespace": namespace,
                "key": key,
                "message": f"Stored memory: {key}",
                "hint": f"Use recall('{content[:50]}...') to retrieve this later.",
            })

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return remember


def create_recall_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool for recalling memories."""
    service = MemoryService(storage)

    def recall(
        query: str,
        namespace: str | None = None,
        limit: int = 5,
    ) -> str:
        """Search your long-term memory for relevant information.

        Use this at the START of any analysis to recall:
        - Previous user preferences about formatting or analysis approach
        - Business facts and data insights (shared across sessions)
        - Corrections from the user about how to interpret data

        Args:
            query: What to search for (e.g., "user date preferences", "revenue calculation")
            namespace: Optional namespace to search within:
                - "shared_knowledge": Business facts + data insights (SHARED)
                - "user_preferences": Session-specific preferences
                - "corrections": User corrections
                - None to search all namespaces
            limit: Maximum number of memories to return (default: 5)

        Returns:
            JSON string with matching memories sorted by relevance.
        """
        try:
            results = service.recall(
                db_connection_id=db_connection.id,
                query=query,
                namespace=namespace,
                limit=limit,
            )

            if not results:
                return json.dumps({
                    "success": True,
                    "message": "No relevant memories found.",
                    "memories": [],
                    "hint": "Query the database for actual data. Memories are context hints only.",
                })

            memory_list = []
            stale_count = 0
            for r in results:
                is_stale = _is_potentially_stale(r.memory.created_at, r.memory.namespace)
                if is_stale:
                    stale_count += 1

                memory_entry = {
                    "namespace": r.memory.namespace,
                    "key": r.memory.key,
                    "content": r.memory.value.get("content", str(r.memory.value)),
                    "relevance_score": round(r.score, 2),
                    "importance": r.memory.importance,
                    "access_count": r.memory.access_count,
                    "created_at": r.memory.created_at,
                    "age": _calculate_age(r.memory.created_at),
                    "potentially_stale": is_stale,
                }

                # Include source question if available
                source_question = r.memory.value.get("source_question")
                if source_question:
                    memory_entry["source_question"] = source_question

                memory_list.append(memory_entry)

            result = {
                "success": True,
                "query": query,
                "total": len(memory_list),
                "memories": memory_list,
                "recommendation": "Use these as context hints. Still query the database for actual data.",
                "critical_note": "Memories are CONTEXT only - always query the database for data answers.",
            }

            # Add warning if some memories are stale
            if stale_count > 0:
                result["stale_warning"] = (
                    f"{stale_count} memory(ies) may be outdated. "
                    "Verify with user if still relevant, and use forget() to remove if outdated."
                )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return recall


def create_forget_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool for deleting memories."""
    service = MemoryService(storage)

    def forget(namespace: str, key: str) -> str:
        """Remove a memory that is no longer relevant or was incorrect.

        Use this to:
        - Remove outdated information
        - Delete incorrect memories
        - Clear preferences that are no longer valid

        Args:
            namespace: Category of memory (e.g., "user_preferences", "business_facts")
            key: Unique identifier of the memory to forget

        Returns:
            JSON string confirming deletion or indicating memory was not found.
        """
        try:
            success = service.forget(db_connection.id, namespace, key)

            if success:
                return json.dumps({
                    "success": True,
                    "action": "forgotten",
                    "namespace": namespace,
                    "key": key,
                    "message": f"Memory '{key}' has been deleted from '{namespace}'.",
                })
            else:
                return json.dumps({
                    "success": False,
                    "namespace": namespace,
                    "key": key,
                    "message": f"Memory '{key}' not found in namespace '{namespace}'.",
                    "hint": "Use recall() to search for memories.",
                })

        except Exception as e:
            logger.error(f"Error forgetting memory: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return forget


def create_list_memories_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool for listing memories."""
    service = MemoryService(storage)

    def list_memories(namespace: str | None = None, limit: int = 20) -> str:
        """List all stored memories, optionally filtered by namespace.

        Use this to see what you have remembered about this database connection.

        Args:
            namespace: Optional namespace to filter by:
                - "shared_knowledge": Business facts + data insights (SHARED)
                - "user_preferences": Session-specific preferences
                - "corrections": User corrections
                - None to list all namespaces
            limit: Maximum number of memories to return (default: 20)

        Returns:
            JSON string with stored memories.
        """
        try:
            memories = service.list_memories(
                db_connection_id=db_connection.id,
                namespace=namespace,
                limit=limit,
            )

            if not memories:
                return json.dumps({
                    "success": True,
                    "message": "No memories stored yet.",
                    "memories": [],
                    "hint": "Use remember() to store insights for future use.",
                })

            # Group by namespace for better readability
            by_namespace: dict = {}
            for m in memories:
                if m.namespace not in by_namespace:
                    by_namespace[m.namespace] = []
                by_namespace[m.namespace].append({
                    "key": m.key,
                    "content": m.value.get("content", str(m.value)),
                    "importance": m.importance,
                    "access_count": m.access_count,
                    "created_at": m.created_at,
                })

            return json.dumps({
                "success": True,
                "total": len(memories),
                "memories_by_namespace": by_namespace,
            }, indent=2)

        except Exception as e:
            logger.error(f"Error listing memories: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return list_memories


def create_recall_for_question_tool(
    db_connection: DatabaseConnection, storage: Storage
):
    """Create tool to automatically recall memories relevant to a user's question."""
    service = MemoryService(storage)

    def recall_for_question(question: str) -> str:
        """Automatically recall memories that might be relevant to a user's question.

        CALL THIS at the START of any analysis to check for relevant memories
        before proceeding. This helps apply previously learned preferences,
        facts, and insights.

        Args:
            question: The user's question or analysis request

        Returns:
            JSON with relevant memories and recommendations.
        """
        try:
            # Search across all namespaces
            results = service.recall(
                db_connection_id=db_connection.id,
                query=question,
                namespace=None,
                limit=5,
            )

            if not results:
                return json.dumps({
                    "success": True,
                    "message": "No relevant memories found for this question.",
                    "memories": [],
                    "recommendation": "Query the database to find the answer. Do not assume data doesn't exist.",
                })

            # Categorize and format memories
            # Note: shared_knowledge combines legacy business_facts and data_insights
            categorized: dict = {
                "shared_knowledge": [],  # Business facts + data insights (shared)
                "user_preferences": [],
                "corrections": [],
                "other": [],
            }
            # Legacy namespace mapping
            legacy_mapping = {
                "business_facts": "shared_knowledge",
                "data_insights": "shared_knowledge",
            }

            stale_memories = []
            for r in results:
                # Map legacy namespaces to shared_knowledge
                ns = legacy_mapping.get(r.memory.namespace, r.memory.namespace)
                cat = ns if ns in categorized else "other"
                is_stale = _is_potentially_stale(r.memory.created_at, r.memory.namespace)

                memory_entry = {
                    "key": r.memory.key,
                    "content": r.memory.value.get("content", str(r.memory.value)),
                    "relevance": round(r.score, 2),
                    "age": _calculate_age(r.memory.created_at),
                    "created_at": r.memory.created_at,
                }

                # Include source question if available
                source_question = r.memory.value.get("source_question")
                if source_question:
                    memory_entry["source_question"] = source_question[:200]

                if is_stale:
                    memory_entry["potentially_stale"] = True
                    stale_memories.append(f"{r.memory.namespace}/{r.memory.key}")

                categorized[cat].append(memory_entry)

            # Remove empty categories
            categorized = {k: v for k, v in categorized.items() if v}

            # Generate recommendations based on what was found
            recommendations = []
            if categorized.get("user_preferences"):
                recommendations.append(
                    "Apply user preferences found above to your analysis."
                )
            if categorized.get("shared_knowledge"):
                recommendations.append(
                    "Consider the shared business facts and data insights when interpreting results."
                )
            if categorized.get("corrections"):
                recommendations.append(
                    "Apply corrections to avoid previous mistakes."
                )

            result = {
                "success": True,
                "question": question[:200] + "..." if len(question) > 200 else question,
                "relevant_memories": categorized,
                "total_found": sum(len(v) for v in categorized.values()),
                "recommendations": recommendations or ["Apply these memories to your analysis."],
                "critical_note": (
                    "These memories are CONTEXT HINTS only - NOT actual data! "
                    "You MUST query the database to answer data questions. "
                    "Never assume data doesn't exist just because it's not in memory."
                ),
            }

            # Add warning if some memories are stale
            if stale_memories:
                result["stale_warning"] = (
                    f"{len(stale_memories)} memory(ies) may be outdated: {', '.join(stale_memories[:3])}. "
                    "Verify with user if still relevant, and use forget() to remove if outdated."
                )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error recalling memories for question: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "recommendation": "Proceed with standard approach.",
            })

    return recall_for_question
