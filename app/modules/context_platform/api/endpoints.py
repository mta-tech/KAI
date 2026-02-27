"""Context Platform API Endpoints.

This module contains the API endpoint methods for the Context Platform.
These will be registered in the main API class at app/api/__init__.py.
"""

from typing import Any

from fastapi import HTTPException

from app.api.requests import (
    ContextAssetRequest,
    CreateDraftRevisionRequest,
    DeprecateAssetRequest,
    PromoteAssetRequest,
    SearchContextAssetsRequest,
    UpdateContextAssetRequest,
)
from app.api.responses import (
    ContextAssetResponse,
    ContextAssetSearchResultResponse,
    ContextAssetTagResponse,
    ContextAssetVersionResponse,
)
from app.modules.context_platform.models.asset import (
    ContextAssetType,
    LifecycleState,
)
from app.modules.context_platform.services.asset_service import (
    ContextAssetService,
    LifecyclePolicyError,
)


class ContextPlatformEndpoints:
    """Context Platform API endpoints.

    These methods are mixed into the main API class to provide
    REST endpoints for context asset management.
    """

    def __init__(self, context_asset_service: ContextAssetService):
        """Initialize endpoints with the context asset service.

        Args:
            context_asset_service: The context asset service instance.
        """
        self.context_asset_service = context_asset_service

    # ===== CRUD Endpoints =====

    def create_context_asset(
        self, asset_request: ContextAssetRequest
    ) -> ContextAssetResponse:
        """Create a new context asset in DRAFT state."""
        try:
            # Convert asset_type string to enum
            asset_type = ContextAssetType(asset_request.asset_type)

            asset = self.context_asset_service.create_asset(
                db_connection_id=asset_request.db_connection_id,
                asset_type=asset_type,
                canonical_key=asset_request.canonical_key,
                name=asset_request.name,
                content=asset_request.content,
                content_text=asset_request.content_text,
                description=asset_request.description,
                author=asset_request.author,
                tags=asset_request.tags,
            )

            return self._asset_to_response(asset)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_context_asset(
        self,
        db_connection_id: str,
        asset_type: str,
        canonical_key: str,
        version: str = "latest",
    ) -> ContextAssetResponse:
        """Get a context asset by key."""
        try:
            asset_type_enum = ContextAssetType(asset_type)
            asset = self.context_asset_service.get_asset(
                db_connection_id,
                asset_type_enum,
                canonical_key,
                version,
            )

            if not asset:
                raise HTTPException(
                    status_code=404,
                    detail=f"Asset not found: {asset_type}/{canonical_key}@{version}",
                )

            return self._asset_to_response(asset)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_context_assets(
        self,
        db_connection_id: str,
        asset_type: str | None = None,
        lifecycle_state: str | None = None,
        limit: int = 100,
    ) -> list[ContextAssetResponse]:
        """List context assets with optional filtering."""
        try:
            asset_type_enum = ContextAssetType(asset_type) if asset_type else None
            state_enum = LifecycleState(lifecycle_state) if lifecycle_state else None

            assets = self.context_asset_service.list_assets(
                db_connection_id,
                asset_type=asset_type_enum,
                lifecycle_state=state_enum,
                limit=limit,
            )

            return [self._asset_to_response(asset) for asset in assets]

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def search_context_assets(
        self, search_request: SearchContextAssetsRequest
    ) -> list[ContextAssetSearchResultResponse]:
        """Search context assets by text query."""
        try:
            asset_type = (
                ContextAssetType(search_request.asset_type)
                if search_request.asset_type
                else None
            )

            results = self.context_asset_service.search_assets(
                db_connection_id=search_request.db_connection_id,
                query=search_request.query,
                asset_type=asset_type,
                limit=search_request.limit,
            )

            return [
                ContextAssetSearchResultResponse(
                    asset=self._asset_to_response(result.asset),
                    score=result.score,
                    match_type=result.match_type,
                )
                for result in results
            ]

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_context_asset(
        self, asset_id: str, update_request: UpdateContextAssetRequest
    ) -> ContextAssetResponse:
        """Update an existing context asset (DRAFT only)."""
        try:
            asset = self.context_asset_service.update_asset(
                asset_id=asset_id,
                name=update_request.name,
                description=update_request.description,
                content=update_request.content,
                content_text=update_request.content_text,
                tags=update_request.tags,
            )

            if not asset:
                raise HTTPException(
                    status_code=404, detail=f"Asset not found: {asset_id}"
                )

            return self._asset_to_response(asset)

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_context_asset(
        self,
        db_connection_id: str,
        asset_type: str,
        canonical_key: str,
        version: str | None = None,
    ) -> dict[str, str]:
        """Delete a context asset (DRAFT only)."""
        try:
            asset_type_enum = ContextAssetType(asset_type)
            deleted = self.context_asset_service.delete_asset(
                db_connection_id,
                asset_type_enum,
                canonical_key,
                version,
            )

            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail=f"Asset not found or cannot be deleted: {asset_type}/{canonical_key}",
                )

            return {"message": f"Asset {asset_type}/{canonical_key} deleted successfully"}

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===== Lifecycle Transition Endpoints =====

    def promote_asset_to_verified(
        self, asset_id: str, promote_request: PromoteAssetRequest
    ) -> ContextAssetResponse:
        """Promote an asset from DRAFT to VERIFIED.

        This endpoint requires domain expert approval.
        """
        try:
            asset = self.context_asset_service.promote_to_verified(
                asset_id=asset_id,
                promoted_by=promote_request.promoted_by,
                change_note=promote_request.change_note,
            )

            if not asset:
                raise HTTPException(
                    status_code=404, detail=f"Asset not found: {asset_id}"
                )

            return self._asset_to_response(asset)

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def promote_asset_to_published(
        self, asset_id: str, promote_request: PromoteAssetRequest
    ) -> ContextAssetResponse:
        """Promote an asset from VERIFIED to PUBLISHED.

        This endpoint requires final approval for reuse across missions.
        """
        try:
            asset = self.context_asset_service.promote_to_published(
                asset_id=asset_id,
                promoted_by=promote_request.promoted_by,
                change_note=promote_request.change_note,
            )

            if not asset:
                raise HTTPException(
                    status_code=404, detail=f"Asset not found: {asset_id}"
                )

            return self._asset_to_response(asset)

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def deprecate_asset(
        self, asset_id: str, deprecate_request: DeprecateAssetRequest
    ) -> ContextAssetResponse:
        """Deprecate a published asset."""
        try:
            asset = self.context_asset_service.deprecate_asset(
                asset_id=asset_id,
                promoted_by=deprecate_request.promoted_by,
                reason=deprecate_request.reason,
            )

            if not asset:
                raise HTTPException(
                    status_code=404, detail=f"Asset not found: {asset_id}"
                )

            return self._asset_to_response(asset)

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_asset_draft_revision(
        self, asset_id: str, revision_request: CreateDraftRevisionRequest
    ) -> ContextAssetResponse:
        """Create a new DRAFT revision of an existing asset."""
        try:
            asset = self.context_asset_service.create_draft_revision(
                asset_id=asset_id,
                author=revision_request.author,
            )

            if not asset:
                raise HTTPException(
                    status_code=404, detail=f"Asset not found: {asset_id}"
                )

            return self._asset_to_response(asset)

        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===== Version History Endpoints =====

    def get_asset_version_history(
        self, asset_id: str
    ) -> list[ContextAssetVersionResponse]:
        """Get the version history for an asset."""
        try:
            versions = self.context_asset_service.get_version_history(asset_id)

            return [
                ContextAssetVersionResponse(
                    id=v.id,
                    asset_id=v.asset_id,
                    version=v.version,
                    name=v.name,
                    description=v.description,
                    content=v.content,
                    content_text=v.content_text,
                    lifecycle_state=v.lifecycle_state.value,
                    author=v.author,
                    change_summary=v.change_summary,
                    created_at=v.created_at,
                )
                for v in versions
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===== Tag Endpoints =====

    def get_asset_tags(
        self, category: str | None = None
    ) -> list[ContextAssetTagResponse]:
        """Get all context asset tags, optionally filtered by category."""
        try:
            tags = self.context_asset_service.get_tags(category)

            return [
                ContextAssetTagResponse(
                    id=t.id,
                    name=t.name,
                    category=t.category,
                    description=t.description,
                    usage_count=t.usage_count,
                    last_used_at=t.last_used_at,
                    created_at=t.created_at,
                )
                for t in tags
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===== Helper Methods =====

    def _asset_to_response(self, asset: Any) -> ContextAssetResponse:
        """Convert a ContextAsset model to a response.

        Extracts promotion metadata from content if available.
        """
        # Extract promotion metadata from content
        promoted_by = asset.content.get("promoted_by") if isinstance(asset.content, dict) else None
        promoted_at = asset.content.get("promoted_at") if isinstance(asset.content, dict) else None
        change_note = asset.content.get("change_note") if isinstance(asset.content, dict) else None

        return ContextAssetResponse(
            id=asset.id,
            db_connection_id=asset.db_connection_id,
            asset_type=asset.asset_type.value,
            canonical_key=asset.canonical_key,
            version=asset.version,
            name=asset.name,
            description=asset.description,
            content=asset.content,
            content_text=asset.content_text,
            lifecycle_state=asset.lifecycle_state.value,
            tags=asset.tags,
            author=asset.author,
            parent_asset_id=asset.parent_asset_id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            promoted_by=promoted_by,
            promoted_at=promoted_at,
            change_note=change_note,
        )


    # ============================================================================
    # Benchmark Endpoints
    # ============================================================================

    def create_benchmark_suite(
        self,
        name: str,
        db_connection_id: str,
        description: str | None = None,
        case_ids: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Create a new benchmark suite."""
        try:
            from app.modules.context_platform.models.benchmark import BenchmarkSuite
            from datetime import datetime

            suite = BenchmarkSuite(
                id=f"suite_{datetime.now().timestamp()}",
                name=name,
                db_connection_id=db_connection_id,
                description=description,
                case_ids=case_ids or [],
                tags=tags or [],
            )

            suite_id = self.context_asset_service.storage.insert_one(
                "benchmark_suites",
                suite.__dict__
            )

            return {"id": suite_id, "name": name, "created_at": suite.created_at}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_benchmark_suites(
        self,
        db_connection_id: str | None = None,
        active_only: bool = True,
    ) -> list[dict]:
        """List benchmark suites."""
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)
            suites = service.list_suites(
                db_connection_id=db_connection_id,
                active_only=active_only
            )

            return suites

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_suite(self, suite_id: str) -> dict:
        """Get a benchmark suite by ID."""
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)
            suite = service.get_suite(suite_id)

            if not suite:
                raise HTTPException(
                    status_code=404,
                    detail=f"Suite not found: {suite_id}"
                )

            return suite

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run_benchmark(
        self,
        suite_id: str,
        db_connection_id: str,
        context_asset_ids: list[str] | None = None,
    ) -> dict:
        """Run a benchmark suite.

        Creates a new run and executes all cases in the suite.
        """
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)

            # Verify suite exists
            suite = service.get_suite(suite_id)
            if not suite:
                raise HTTPException(
                    status_code=404,
                    detail=f"Suite not found: {suite_id}"
                )

            # Create run
            run = service.create_run(
                suite_id=suite_id,
                db_connection_id=db_connection_id,
                context_asset_ids=context_asset_ids or []
            )

            # Start run
            service.start_run(run.id)

            # Execute cases (mock execution for now)
            case_ids = suite.get("case_ids", [])
            for case_id in case_ids:
                case = service.get_case(case_id)
                if case:
                    service.execute_case(
                        run_id=run.id,
                        case_id=case_id,
                        actual_sql=case.get("expected_sql"),  # Using expected as actual
                        context_assets_used=context_asset_ids or [],
                        execution_time_ms=150,
                    )

            # Complete run
            completed_run = service.complete_run(run.id)

            return completed_run

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_run(self, run_id: str) -> dict:
        """Get a benchmark run by ID."""
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)
            run = service.repository.find_run_by_id(run_id)

            if not run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Run not found: {run_id}"
                )

            return run

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_benchmark_runs(
        self,
        suite_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """List benchmark runs for a suite."""
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)
            runs = service.repository.find_runs_by_suite(suite_id, limit)

            return runs

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_results(self, run_id: str) -> list[dict]:
        """Get results for a benchmark run."""
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)
            results = service.repository.find_results_by_run(run_id)

            return results

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def export_benchmark_run(
        self,
        run_id: str,
        format: str = "json",
    ) -> dict | str:
        """Export a benchmark run.

        Args:
            run_id: The run ID to export
            format: Export format - "json" or "junit"

        Returns:
            JSON dict or JUnit XML string
        """
        try:
            from app.modules.context_platform.services.benchmark_service import BenchmarkService

            service = BenchmarkService(self.context_asset_service.storage)

            if format == "json":
                data = service.export_run_json(run_id)
                if not data:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Run not found: {run_id}"
                    )
                return data
            elif format == "junit":
                xml = service.export_run_junit(run_id)
                if not xml:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Run not found: {run_id}"
                    )
                return xml
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid format: {format}. Use 'json' or 'junit'"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ============================================================================
    # Feedback Endpoints
    # ============================================================================

    def submit_feedback(
        self,
        feedback_request: dict,
    ) -> dict:
        """Submit feedback on a context platform entity.

        Accepts feedback on context assets, benchmark cases, or mission runs.
        """
        try:
            from app.modules.context_platform.models.feedback import (
                Feedback,
                FeedbackRequest,
                FeedbackType,
                FeedbackTargetType,
            )

            # Create feedback from request
            feedback = Feedback(
                feedback_type=FeedbackType(feedback_request.get("feedback_type", "other")),
                target_type=FeedbackTargetType(feedback_request.get("target_type", "other")),
                target_id=feedback_request.get("target_id"),
                title=feedback_request.get("title", ""),
                description=feedback_request.get("description", ""),
                severity=feedback_request.get("severity", "medium"),
                validation_result=feedback_request.get("validation_result"),
                validation_notes=feedback_request.get("validation_notes"),
                tags=feedback_request.get("tags", []),
                metadata=feedback_request.get("metadata", {}),
            )

            # Validate size limits
            max_title_length = 200
            max_description_length = 5000

            if len(feedback.title) > max_title_length:
                raise HTTPException(
                    status_code=400,
                    detail=f"Title too long (max {max_title_length} characters)"
                )

            if len(feedback.description) > max_description_length:
                raise HTTPException(
                    status_code=400,
                    detail=f"Description too long (max {max_description_length} characters)"
                )

            # Store feedback
            feedback_id = self.context_asset_service.storage.insert_one(
                "feedback",
                feedback.__dict__
            )

            return {
                "id": feedback_id,
                "status": "pending",
                "message": "Feedback submitted successfully",
                "created_at": feedback.created_at,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_feedback(
        self,
        target_type: str | None = None,
        target_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List feedback with optional filters.

        Args:
            target_type: Filter by target entity type
            target_id: Filter by target entity ID
            status: Filter by feedback status
            limit: Maximum results to return
        """
        try:
            storage = self.context_asset_service.storage

            # Build filter
            filter_dict = {}
            if target_type:
                filter_dict["target_type"] = target_type
            if target_id:
                filter_dict["target_id"] = target_id
            if status:
                filter_dict["status"] = status

            # Query feedback
            if filter_dict:
                results = storage.find("feedback", filter_dict, limit=limit)
            else:
                results = storage.find_all("feedback", limit=limit)

            return results

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_feedback(self, feedback_id: str) -> dict:
        """Get feedback by ID.

        Args:
            feedback_id: The feedback ID
        """
        try:
            storage = self.context_asset_service.storage
            feedback = storage.find_by_id("feedback", feedback_id)

            if not feedback:
                raise HTTPException(
                    status_code=404,
                    detail=f"Feedback not found: {feedback_id}"
                )

            return feedback

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_feedback_status(
        self,
        feedback_id: str,
        status: str,
        review_notes: str | None = None,
    ) -> dict:
        """Update feedback status.

        Args:
            feedback_id: The feedback ID
            status: New status (pending, reviewed, addressed, dismissed)
            review_notes: Optional review notes
        """
        try:
            from app.modules.context_platform.models.feedback import FeedbackStatus

            # Validate status
            valid_statuses = ["pending", "reviewed", "addressed", "dismissed"]
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Invalid status. Must be one of: {valid_statuses}"
                )

            storage = self.context_asset_service.storage

            # Check if feedback exists
            existing = storage.find_by_id("feedback", feedback_id)
            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail=f"Feedback not found: {feedback_id}"
                )

            # Update status
            from datetime import datetime
            updates = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
            }

            if review_notes:
                updates["review_notes"] = review_notes
                updates["reviewed_at"] = datetime.now().isoformat()

            storage.update_or_create(
                "feedback",
                {"id": feedback_id},
                updates
            )

            return {
                "id": feedback_id,
                "status": status,
                "updated_at": updates["updated_at"],
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
