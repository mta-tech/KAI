"""Context store tools for the autonomous agent.

These tools allow the agent to check if a natural language question
already has a verified SQL query in the context store.
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)


def create_lookup_verified_sql_tool(db_connection_id: str, storage):
    """Create a tool to lookup verified SQL for a question.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Lookup function.
    """

    def lookup_verified_sql(question: str) -> str:
        """Check if a question has a verified SQL query in the context store.

        Use this tool BEFORE generating SQL to check if the question
        or a similar question already has a verified SQL query.
        This can save time and ensure consistent results.

        Args:
            question: The natural language question to look up.

        Returns:
            JSON with verified SQL if found, or not found message.

        Example:
            question = "What are the total sales by region?"
            result = lookup_verified_sql(question)
            # If found: {"found": true, "sql": "SELECT ...", "similarity": 0.98}
            # If not found: {"found": false, "message": "No verified SQL found"}
        """
        try:
            from app.modules.context_store.services import ContextStoreService
            service = ContextStoreService(storage)

            # First try exact match
            exact_match = service.retrieve_exact_prompt(db_connection_id, question)
            if exact_match:
                return json.dumps({
                    "found": True,
                    "match_type": "exact",
                    "original_question": exact_match.prompt_text,
                    "sql": exact_match.sql,
                    "similarity": 1.0,
                    "context_id": exact_match.id,
                })

            # Try semantic search for similar questions
            similar_results = service.get_semantic_context_stores(
                db_connection_id=db_connection_id,
                prompt=question,
                top_k=3,
            )

            if similar_results:
                # Filter for high similarity matches (>= 0.85)
                high_matches = [r for r in similar_results if r.get("score", 0) >= 0.85]

                if high_matches:
                    best_match = high_matches[0]
                    return json.dumps({
                        "found": True,
                        "match_type": "semantic",
                        "original_question": best_match["prompt_text"],
                        "sql": best_match["sql"],
                        "similarity": round(best_match["score"], 3),
                        "note": "This is a semantically similar question. Verify the SQL is appropriate.",
                    })

                # Return suggestions for lower matches
                if similar_results:
                    suggestions = [
                        {
                            "question": r["prompt_text"],
                            "sql": r["sql"],
                            "similarity": round(r.get("score", 0), 3),
                        }
                        for r in similar_results[:3]
                    ]
                    return json.dumps({
                        "found": False,
                        "message": "No exact or high-similarity match found",
                        "suggestions": suggestions,
                        "note": "Consider these similar verified queries for reference",
                    })

            return json.dumps({
                "found": False,
                "message": "No verified SQL found for this question",
                "recommendation": "Generate a new SQL query",
            })

        except Exception as e:
            logger.error(f"Error looking up verified SQL: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return lookup_verified_sql


def create_save_verified_sql_tool(db_connection_id: str, storage):
    """Create a tool to save a verified SQL query to the context store.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Save function.
    """

    def save_verified_sql(question: str, sql: str, metadata: str | None = None) -> str:
        """Save a verified SQL query to the context store for future reuse.

        Use this tool to store a SQL query that has been verified to work
        correctly for a given question. This allows future queries to
        reuse the verified SQL.

        Args:
            question: The natural language question.
            sql: The verified SQL query that answers the question.
            metadata: Optional JSON string with additional metadata.

        Returns:
            JSON with save result.

        Example:
            question = "What are the total sales by region?"
            sql = "SELECT region, SUM(amount) FROM sales GROUP BY region"
            result = save_verified_sql(question, sql)
        """
        try:
            from app.api.requests import ContextStoreRequest
            from app.modules.context_store.services import ContextStoreService

            service = ContextStoreService(storage)

            # Check if already exists
            existing = service.retrieve_exact_prompt(db_connection_id, question)
            if existing:
                return json.dumps({
                    "success": False,
                    "message": "A verified SQL already exists for this exact question",
                    "existing_sql": existing.sql,
                    "context_id": existing.id,
                })

            # Parse metadata if provided
            meta_dict = None
            if metadata:
                try:
                    meta_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    meta_dict = {"note": metadata}

            # Create the context store entry
            request = ContextStoreRequest(
                db_connection_id=db_connection_id,
                prompt_text=question,
                sql=sql,
                metadata=meta_dict,
            )

            context_store = service.create_context_store(request)

            return json.dumps({
                "success": True,
                "message": "Verified SQL saved successfully",
                "context_id": context_store.id,
                "question": question,
                "sql": sql,
            })

        except Exception as e:
            logger.error(f"Error saving verified SQL: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return save_verified_sql


def create_list_verified_queries_tool(db_connection_id: str, storage):
    """Create a tool to list verified SQL queries in the context store.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        List function.
    """

    def list_verified_queries(limit: int = 20) -> str:
        """List verified SQL queries in the context store.

        Use this tool to see what verified queries are available
        for this database.

        Args:
            limit: Maximum number of queries to return (default 20).

        Returns:
            JSON with list of verified queries.
        """
        try:
            from app.modules.context_store.services import ContextStoreService
            service = ContextStoreService(storage)
            context_stores = service.get_context_stores(db_connection_id)

            queries = [
                {
                    "id": cs.id,
                    "question": cs.prompt_text,
                    "sql": cs.sql[:200] + "..." if len(cs.sql) > 200 else cs.sql,
                    "created_at": cs.created_at,
                }
                for cs in context_stores[:limit]
            ]

            return json.dumps({
                "success": True,
                "count": len(queries),
                "total_available": len(context_stores),
                "queries": queries,
            })

        except Exception as e:
            logger.error(f"Error listing verified queries: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return list_verified_queries


def create_search_verified_queries_tool(db_connection_id: str, storage):
    """Create a tool to search for similar verified queries.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Search function.
    """

    def search_verified_queries(search_text: str, top_k: int = 5) -> str:
        """Search for similar verified SQL queries.

        Use this tool to find verified queries that are similar to
        a given search text or question.

        Args:
            search_text: Text to search for similar queries.
            top_k: Number of results to return (default 5).

        Returns:
            JSON with matching verified queries.
        """
        try:
            from app.modules.context_store.services import ContextStoreService
            service = ContextStoreService(storage)
            results = service.get_semantic_context_stores(
                db_connection_id=db_connection_id,
                prompt=search_text,
                top_k=top_k,
            )

            if not results:
                return json.dumps({
                    "success": True,
                    "count": 0,
                    "message": "No similar verified queries found",
                    "queries": [],
                })

            queries = [
                {
                    "question": r["prompt_text"],
                    "sql": r["sql"],
                    "similarity": round(r.get("score", 0), 3),
                }
                for r in results
            ]

            return json.dumps({
                "success": True,
                "count": len(queries),
                "queries": queries,
            })

        except Exception as e:
            logger.error(f"Error searching verified queries: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return search_verified_queries


def create_delete_verified_sql_tool(db_connection_id: str, storage):
    """Create a tool to delete a verified SQL from the context store.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Delete function.
    """

    def delete_verified_sql(context_id: str) -> str:
        """Delete a verified SQL query from the context store.

        Use this tool to remove an incorrect or outdated verified query.

        Args:
            context_id: The ID of the context store entry to delete.

        Returns:
            JSON with deletion result.
        """
        try:
            from app.modules.context_store.services import ContextStoreService
            service = ContextStoreService(storage)

            # Verify it exists and belongs to this db_connection
            context_store = service.get_context_store(context_id)
            if context_store.db_connection_id != db_connection_id:
                return json.dumps({
                    "success": False,
                    "error": "Context store entry does not belong to this database",
                })

            service.delete_context_store(context_id)

            return json.dumps({
                "success": True,
                "message": f"Verified SQL {context_id} deleted successfully",
            })

        except Exception as e:
            logger.error(f"Error deleting verified SQL: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return delete_verified_sql
