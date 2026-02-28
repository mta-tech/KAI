"""Context platform tools for the autonomous agent.

These tools give the agent access to published, lifecycle-managed context
assets from the Context Platform. Published assets are expert-verified and
should be preferred over raw unversioned data when available.
"""

from __future__ import annotations

import json
import logging

from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection

logger = logging.getLogger(__name__)


def _get_connection_id(db_connection: DatabaseConnection) -> str:
    """Extract connection ID, raising if missing."""
    if db_connection.id is None:
        raise ValueError("Database connection has no ID")
    return db_connection.id


def create_get_published_instructions_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to get published instruction assets."""

    def get_published_instructions() -> str:
        """Get all PUBLISHED instruction assets for the current database.

        Published instructions are expert-verified rules that have been
        promoted through the lifecycle (draft -> verified -> published).
        They should be given higher priority than unversioned instructions.

        Returns:
            JSON string with published instruction assets.
        """
        try:
            from app.modules.context_platform.models.asset import (
                ContextAssetType,
                LifecycleState,
            )
            from app.modules.context_platform.services.asset_service import (
                ContextAssetService,
            )

            conn_id = _get_connection_id(db_connection)
            service = ContextAssetService(storage)
            assets = service.list_assets(
                db_connection_id=conn_id,
                asset_type=ContextAssetType.INSTRUCTION,
                lifecycle_state=LifecycleState.PUBLISHED,
                limit=100,
            )

            if not assets:
                return json.dumps({
                    "success": True,
                    "message": "No published instruction assets found.",
                    "instructions": [],
                })

            _track_reuse(storage, assets, "mission")

            return json.dumps({
                "success": True,
                "total": len(assets),
                "instructions": [
                    {
                        "id": a.id,
                        "key": a.canonical_key,
                        "name": a.name,
                        "description": a.description,
                        "content": a.content,
                        "version": a.version,
                        "tags": a.tags,
                    }
                    for a in assets
                ],
            })
        except Exception as e:
            logger.error(f"Error fetching published instructions: {e}")
            return json.dumps({"success": False, "error": str(e)})

    get_published_instructions.__name__ = "get_published_instructions"
    return get_published_instructions


def create_get_published_glossary_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to get published glossary assets."""

    def get_published_glossary() -> str:
        """Get all PUBLISHED glossary assets for the current database.

        Published glossary terms are expert-verified business definitions
        promoted through the lifecycle. Use these for accurate business
        terminology when generating SQL.

        Returns:
            JSON string with published glossary assets.
        """
        try:
            from app.modules.context_platform.models.asset import (
                ContextAssetType,
                LifecycleState,
            )
            from app.modules.context_platform.services.asset_service import (
                ContextAssetService,
            )

            conn_id = _get_connection_id(db_connection)
            service = ContextAssetService(storage)
            assets = service.list_assets(
                db_connection_id=conn_id,
                asset_type=ContextAssetType.GLOSSARY,
                lifecycle_state=LifecycleState.PUBLISHED,
                limit=100,
            )

            if not assets:
                return json.dumps({
                    "success": True,
                    "message": "No published glossary assets found.",
                    "glossary": [],
                })

            _track_reuse(storage, assets, "mission")

            return json.dumps({
                "success": True,
                "total": len(assets),
                "glossary": [
                    {
                        "id": a.id,
                        "key": a.canonical_key,
                        "name": a.name,
                        "description": a.description,
                        "content": a.content,
                        "version": a.version,
                        "tags": a.tags,
                    }
                    for a in assets
                ],
            })
        except Exception as e:
            logger.error(f"Error fetching published glossary: {e}")
            return json.dumps({"success": False, "error": str(e)})

    get_published_glossary.__name__ = "get_published_glossary"
    return get_published_glossary


def create_search_published_assets_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to search published context assets by query."""

    def search_published_assets(query: str, asset_type: str | None = None) -> str:
        """Search for PUBLISHED context assets relevant to the current question.

        Performs semantic search across all published assets. Use this to find
        domain knowledge that can improve SQL generation accuracy.

        Args:
            query: Natural language search query (e.g. "revenue calculation").
            asset_type: Optional filter: "instruction", "glossary",
                "table_description", or "skill".

        Returns:
            JSON string with matching published assets and relevance scores.
        """
        try:
            from app.modules.context_platform.models.asset import ContextAssetType
            from app.modules.context_platform.services.asset_service import (
                ContextAssetService,
            )

            conn_id = _get_connection_id(db_connection)
            service = ContextAssetService(storage)
            type_enum = ContextAssetType(asset_type) if asset_type else None

            results = service.search_assets(
                db_connection_id=conn_id,
                query=query,
                asset_type=type_enum,
                limit=10,
            )

            if not results:
                return json.dumps({
                    "success": True,
                    "message": f"No published assets found matching '{query}'.",
                    "results": [],
                })

            _track_reuse(storage, [r.asset for r in results], "mission")

            return json.dumps({
                "success": True,
                "total": len(results),
                "results": [
                    {
                        "id": r.asset.id,
                        "asset_type": (
                            r.asset.asset_type
                            if isinstance(r.asset.asset_type, str)
                            else r.asset.asset_type.value
                        ),
                        "key": r.asset.canonical_key,
                        "name": r.asset.name,
                        "description": r.asset.description,
                        "content": r.asset.content,
                        "version": r.asset.version,
                        "score": r.score,
                        "match_type": r.match_type,
                        "tags": r.asset.tags,
                    }
                    for r in results
                ],
            })
        except Exception as e:
            logger.error(f"Error searching published assets: {e}")
            return json.dumps({"success": False, "error": str(e)})

    search_published_assets.__name__ = "search_published_assets"
    return search_published_assets


def create_submit_asset_feedback_tool(storage: Storage):
    """Create a tool for the agent to report quality issues on context assets."""

    def submit_asset_feedback(
        asset_id: str,
        feedback_type: str,
        title: str,
        description: str,
    ) -> str:
        """Submit feedback on a context asset the agent encountered.

        Use this when you find that a published asset (instruction, glossary,
        etc.) produced incorrect or misleading results during analysis.

        Args:
            asset_id: The ID of the context asset (from search/list results).
            feedback_type: One of "correction", "improvement", "confirmation".
            title: Short summary of the feedback (max 200 chars).
            description: Detailed explanation of the issue.

        Returns:
            JSON confirmation of feedback submission.
        """
        try:
            from app.modules.context_platform.models.feedback import (
                Feedback,
                FeedbackTargetType,
                FeedbackType,
            )

            feedback = Feedback(
                feedback_type=FeedbackType(feedback_type),
                target_type=FeedbackTargetType("context_asset"),
                target_id=asset_id,
                title=title[:200],
                description=description[:5000],
                severity="medium",
                tags=["agent-generated"],
                metadata={"source": "autonomous_agent"},
            )

            feedback_id = storage.insert_one("feedback", feedback.__dict__)
            return json.dumps({
                "success": True,
                "feedback_id": str(feedback_id),
                "message": "Feedback submitted successfully.",
            })
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return json.dumps({"success": False, "error": str(e)})

    submit_asset_feedback.__name__ = "submit_asset_feedback"
    return submit_asset_feedback


def _track_reuse(storage: Storage, assets: list, reuse_type: str) -> None:
    """Fire-and-forget telemetry for asset reuse during agent execution."""
    try:
        from app.modules.context_platform.services.telemetry_service import (
            TelemetryService,
        )

        telemetry = TelemetryService(storage)
        for asset in assets:
            asset_type = asset.asset_type
            if not isinstance(asset_type, str):
                asset_type = asset_type.value
            telemetry.track_asset_reuse(
                asset_id=asset.id or "",
                asset_type=asset_type,
                reuse_type=reuse_type,
            )
    except Exception:
        # Telemetry is best-effort — never block agent execution
        pass
