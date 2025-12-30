"""Dashboard repository for Typesense storage."""
from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime
from typing import Optional

from app.data.db.storage import Storage
from app.modules.dashboard.models import Dashboard, DashboardLayout, Widget

logger = logging.getLogger(__name__)


class DashboardRepository:
    """Repository for dashboard CRUD operations with Typesense."""

    COLLECTION = "dashboards"

    def __init__(self, storage: Storage):
        self.storage = storage

    def create(self, dashboard: Dashboard) -> Dashboard:
        """Create a new dashboard."""
        doc = self._to_document(dashboard)
        # storage.insert_one returns the ID as a string
        dashboard.id = str(self.storage.insert_one(self.COLLECTION, doc))
        return dashboard

    def get(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        doc = self.storage.find_one(self.COLLECTION, {"id": dashboard_id})
        if not doc:
            return None
        return self._from_document(doc)

    def get_by_share_token(self, token: str) -> Optional[Dashboard]:
        """Get dashboard by share token."""
        results = self.storage.find(
            self.COLLECTION, {"share_token": token, "is_public": True}
        )
        if not results:
            return None
        return self._from_document(results[0])

    def list_by_connection(self, db_connection_id: str) -> list[Dashboard]:
        """List all dashboards for a database connection."""
        results = self.storage.find(
            self.COLLECTION, {"db_connection_id": db_connection_id}
        )
        return [self._from_document(doc) for doc in results]

    def list_all(self) -> list[Dashboard]:
        """List all dashboards."""
        results = self.storage.find_all(self.COLLECTION)
        return [self._from_document(doc) for doc in results]

    def update(self, dashboard: Dashboard) -> Dashboard:
        """Update an existing dashboard."""
        dashboard.updated_at = datetime.utcnow()
        doc = self._to_document(dashboard)
        self.storage.update_or_create(self.COLLECTION, doc)
        return dashboard

    def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        try:
            self.storage.delete_one(self.COLLECTION, {"id": dashboard_id})
            return True
        except Exception as e:
            logger.warning(f"Failed to delete dashboard {dashboard_id}: {e}")
            return False

    def generate_share_token(self, dashboard_id: str) -> Optional[str]:
        """Generate a share token for a dashboard."""
        dashboard = self.get(dashboard_id)
        if not dashboard:
            return None

        token = secrets.token_urlsafe(32)
        dashboard.share_token = token
        dashboard.is_public = True
        self.update(dashboard)
        return token

    def revoke_share(self, dashboard_id: str) -> bool:
        """Revoke sharing for a dashboard."""
        dashboard = self.get(dashboard_id)
        if not dashboard:
            return False

        dashboard.share_token = None
        dashboard.is_public = False
        self.update(dashboard)
        return True

    def _to_document(self, dashboard: Dashboard) -> dict:
        """Convert Dashboard to Typesense document."""
        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description or "",
            "db_connection_id": dashboard.db_connection_id,
            "layout_json": dashboard.layout.model_dump_json(),
            "filters_json": json.dumps([w.model_dump() for w in dashboard.filters]),
            "theme": dashboard.theme,
            "refresh_interval": dashboard.refresh_interval or 0,
            "is_public": dashboard.is_public,
            "share_token": dashboard.share_token or "",
            "created_at": int(dashboard.created_at.timestamp()),
            "updated_at": int(dashboard.updated_at.timestamp()),
        }

    def _from_document(self, doc: dict) -> Dashboard:
        """Convert Typesense document to Dashboard."""
        # Parse layout
        layout_data = json.loads(doc.get("layout_json", "{}"))
        layout = DashboardLayout(**layout_data) if layout_data else DashboardLayout()

        # Parse filters
        filters_data = json.loads(doc.get("filters_json", "[]"))
        filters = [Widget(**f) for f in filters_data] if filters_data else []

        return Dashboard(
            id=doc["id"],
            name=doc["name"],
            description=doc.get("description") or None,
            db_connection_id=doc["db_connection_id"],
            layout=layout,
            filters=filters,
            theme=doc.get("theme", "default"),
            refresh_interval=doc.get("refresh_interval") or None,
            is_public=doc.get("is_public", False),
            share_token=doc.get("share_token") or None,
            created_at=datetime.fromtimestamp(doc.get("created_at", 0)),
            updated_at=datetime.fromtimestamp(doc.get("updated_at", 0)),
        )


__all__ = ["DashboardRepository"]
