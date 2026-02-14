"""Telemetry service for tracking context asset reuse metrics.

Tracks how context assets are being used across missions and benchmarks
to provide insights into their effectiveness and value.
"""

import uuid
from datetime import datetime
from typing import Any

from app.data.db.storage import Storage


class TelemetryService:
    """Service for tracking and reporting context asset reuse metrics.

    Provides insights into:
    - How often assets are reused
    - Which assets are most valuable
    - ROI on context asset creation effort
    """

    def __init__(self, storage: Storage):
        self.storage = storage
        self.collection = "telemetry_events"

    # ========================================================================
    # Event Tracking
    # ========================================================================

    def track_asset_reuse(
        self,
        asset_id: str,
        asset_type: str,
        reuse_type: str,  # "mission", "benchmark", "validation"
        context: dict | None = None,
        user_id: str | None = None,
    ) -> str:
        """Track a context asset reuse event.

        Args:
            asset_id: ID of the reused asset
            asset_type: Type of asset (instruction, verified_sql, etc.)
            reuse_type: Context where reuse occurred
            context: Additional context about the reuse
            user_id: Optional user who triggered the reuse

        Returns:
            Event ID
        """
        event = {
            "id": f"event_{uuid.uuid4().hex[:12]}",
            "event_type": "asset_reuse",
            "timestamp": datetime.now().isoformat(),
            "asset_id": asset_id,
            "asset_type": asset_type,
            "reuse_type": reuse_type,
            "context": context or {},
            "user_id": user_id,
        }

        event_id = self.storage.insert_one(self.collection, event)
        return event_id

    def track_asset_creation(
        self,
        asset_id: str,
        asset_type: str,
        creation_context: dict | None = None,
        user_id: str | None = None,
    ) -> str:
        """Track context asset creation event.

        Args:
            asset_id: ID of the created asset
            asset_type: Type of asset
            creation_context: How/why the asset was created
            user_id: User who created the asset

        Returns:
            Event ID
        """
        event = {
            "id": f"event_{uuid.uuid4().hex[:12]}",
            "event_type": "asset_creation",
            "timestamp": datetime.now().isoformat(),
            "asset_id": asset_id,
            "asset_type": asset_type,
            "context": creation_context or {},
            "user_id": user_id,
        }

        event_id = self.storage.insert_one(self.collection, event)
        return event_id

    def track_asset_promotion(
        self,
        asset_id: str,
        from_state: str,
        to_state: str,
        user_id: str | None = None,
    ) -> str:
        """Track context asset promotion event.

        Args:
            asset_id: ID of the promoted asset
            from_state: Previous lifecycle state
            to_state: New lifecycle state
            user_id: User who promoted the asset

        Returns:
            Event ID
        """
        event = {
            "id": f"event_{uuid.uuid4().hex[:12]}",
            "event_type": "asset_promotion",
            "timestamp": datetime.now().isoformat(),
            "asset_id": asset_id,
            "from_state": from_state,
            "to_state": to_state,
            "user_id": user_id,
        }

        event_id = self.storage.insert_one(self.collection, event)
        return event_id

    # ========================================================================
    # Metrics Computation
    # ========================================================================

    def get_reuse_count(
        self,
        asset_id: str,
        time_window_days: int | None = None,
    ) -> int:
        """Get total reuse count for an asset.

        Args:
            asset_id: ID of the asset
            time_window_days: Optional time window in days

        Returns:
            Number of reuse events
        """
        from datetime import timedelta

        filter_dict = {
            "event_type": "asset_reuse",
            "asset_id": asset_id,
        }

        if time_window_days:
            cutoff = (datetime.now() - timedelta(days=time_window_days)).isoformat()
            filter_dict["timestamp": f">={cutoff}"

        results = self.storage.find(self.collection, filter_dict, limit=1000)
        return len(results)

    def get_reuse_metrics(
        self,
        asset_type: str | None = None,
        time_window_days: int = 30,
        limit: int = 100,
    ) -> list[dict]:
        """Get reuse metrics for assets.

        Args:
            asset_type: Filter by asset type
            time_window_days: Time window in days
            limit: Maximum results

        Returns:
            List of assets with reuse counts
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=time_window_days)).isoformat()

        # Query all reuse events in time window
        reuse_events = self.storage.find(
            self.collection,
            {
                "event_type": "asset_reuse",
                "timestamp": f">={cutoff}",
            },
            sort=["timestamp:desc"],
            limit=1000,
        )

        # Aggregate by asset
        asset_metrics = {}

        for event in reuse_events:
            asset_id = event.get("asset_id")
            event_asset_type = event.get("asset_type")

            # Filter by type if specified
            if asset_type and event_asset_type != asset_type:
                continue

            if asset_id not in asset_metrics:
                asset_metrics[asset_id] = {
                    "asset_id": asset_id,
                    "asset_type": event_asset_type,
                    "reuse_count": 0,
                    "last_reused_at": None,
                    "reuse_types": set(),
                }

            asset_metrics[asset_id]["reuse_count"] += 1
            if event.get("timestamp"):
                asset_metrics[asset_id]["last_reused_at"] = event["timestamp"]
            asset_metrics[asset_id]["reuse_types"].add(event.get("reuse_type", "unknown"))

        # Convert to list and sort
        result = [
            {
                **metrics,
                "reuse_types": list(metrics["reuse_types"]),
            }
            for metrics in asset_metrics.values()
        ]

        result.sort(key=lambda x: x["reuse_count"], reverse=True)
        return result[:limit]

    def get_asset_kpi(
        self,
        asset_id: str,
        time_window_days: int = 30,
    ) -> dict:
        """Get KPI metrics for a specific asset.

        Args:
            asset_id: ID of the asset
            time_window_days: Time window in days

        Returns:
            KPI metrics including reuse count, creation info, promotions
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=time_window_days)).isoformat()

        # Get all events for this asset
        events = self.storage.find(
            self.collection,
            {
                "asset_id": asset_id,
                "timestamp": f">={cutoff}",
            },
            sort=["timestamp:desc"],
            limit=1000,
        )

        kpi = {
            "asset_id": asset_id,
            "time_window_days": time_window_days,
            "total_events": len(events),
            "reuse_count": 0,
            "creation_count": 0,
            "promotion_count": 0,
            "last_reused_at": None,
            "reuse_by_type": {},  # {mission: 5, benchmark: 2}
        }

        for event in events:
            event_type = event.get("event_type")

            if event_type == "asset_reuse":
                kpi["reuse_count"] += 1
                kpi["last_reused_at"] = event.get("timestamp")

                reuse_type = event.get("reuse_type", "unknown")
                kpi["reuse_by_type"][reuse_type] = kpi["reuse_by_type"].get(reuse_type, 0) + 1

            elif event_type == "asset_creation":
                kpi["creation_count"] += 1

            elif event_type == "asset_promotion":
                kpi["promotion_count"] += 1

        return kpi

    def get_dashboard_metrics(
        self,
        time_window_days: int = 30,
    ) -> dict:
        """Get aggregate metrics for dashboard display.

        Args:
            time_window_days: Time window in days

        Returns:
            Dashboard metrics with totals and breakdowns
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=time_window_days)).isoformat()

        # Get all events in time window
        events = self.storage.find(
            self.collection,
            {
                "timestamp": f">={cutoff}",
            },
            sort=["timestamp:desc"],
            limit=10000,
        )

        metrics = {
            "time_window_days": time_window_days,
            "total_events": len(events),
            "events_by_type": {},  # {asset_creation: 10, asset_reuse: 50, ...}
            "assets_by_type": {},  # {instruction: 15, verified_sql: 8, ...}
            "total_unique_assets": set(),
            "top_reused_assets": [],  # Top 10 by reuse count
        }

        reuse_counts = {}

        for event in events:
            # Count by event type
            event_type = event.get("event_type", "unknown")
            metrics["events_by_type"][event_type] = metrics["events_by_type"].get(event_type, 0) + 1

            # Track unique assets and counts
            if event_type in ["asset_creation", "asset_reuse", "asset_promotion"]:
                asset_id = event.get("asset_id")
                asset_type = event.get("asset_type", "unknown")

                metrics["total_unique_assets"].add(asset_id)
                metrics["assets_by_type"][asset_type] = metrics["assets_by_type"].get(asset_type, 0) + 1

                # Track reuse counts
                if event_type == "asset_reuse":
                    reuse_counts[asset_id] = reuse_counts.get(asset_id, 0) + 1

        # Convert set to count
        metrics["total_unique_assets"] = len(metrics["total_unique_assets"])

        # Get top reused assets
        sorted_assets = sorted(reuse_counts.items(), key=lambda x: x[1], reverse=True)
        metrics["top_reused_assets"] = [
            {"asset_id": asset_id, "reuse_count": count}
            for asset_id, count in sorted_assets[:10]
        ]

        return metrics

    def get_reuse_roi(
        self,
        asset_type: str | None = None,
        min_reuse_count: int = 5,
        time_window_days: int = 30,
    ) -> list[dict]:
        """Get assets with high ROI (reused frequently).

        Args:
            asset_type: Filter by asset type
            min_reuse_count: Minimum reuse count threshold
            time_window_days: Time window in days

        Returns:
            List of high-value assets
        """
        metrics = self.get_reuse_metrics(
            asset_type=asset_type,
            time_window_days=time_window_days,
            limit=1000,
        )

        # Filter by minimum reuse count
        high_roi = [
            asset for asset in metrics
            if asset["reuse_count"] >= min_reuse_count
        ]

        return high_roi
