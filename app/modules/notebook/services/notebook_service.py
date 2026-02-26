"""Notebook CRUD service."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.data.db.storage import Storage
from app.modules.notebook.models import (
    Cell,
    Notebook,
    NotebookCreateRequest,
    NotebookRun,
)

DB_COLLECTION = "notebooks"
RUNS_COLLECTION = "notebook_runs"


class NotebookService:
    """Service for notebook CRUD operations."""

    def __init__(self, storage: Storage) -> None:
        """Initialize notebook service."""
        self.storage = storage

    def create_notebook(self, request: NotebookCreateRequest) -> Notebook:
        """Create a new notebook."""
        notebook_id = str(uuid.uuid4())
        now = datetime.utcnow()

        cells_with_ids = []
        for i, cell in enumerate(request.cells):
            cell_dict = cell.model_dump()
            if not cell_dict.get("id"):
                cell_dict["id"] = f"cell_{i}_{uuid.uuid4().hex[:8]}"
            cells_with_ids.append(Cell(**cell_dict))

        notebook = Notebook(
            id=notebook_id,
            name=request.name,
            description=request.description,
            database_alias=request.database_alias,
            parameters=request.parameters,
            cells=cells_with_ids,
            tags=request.tags,
            created_at=now,
            updated_at=now,
        )

        notebook_dict = notebook.model_dump()
        notebook_dict["created_at"] = notebook_dict["created_at"].isoformat()
        notebook_dict["updated_at"] = notebook_dict["updated_at"].isoformat()

        self.storage.insert_one(DB_COLLECTION, notebook_dict)
        return notebook

    def get_notebook(self, notebook_id: str) -> Notebook | None:
        """Get a notebook by ID."""
        doc = self.storage.find_one(DB_COLLECTION, {"id": notebook_id})
        if not doc:
            return None
        return self._doc_to_notebook(doc)

    def get_notebook_by_name(self, name: str) -> Notebook | None:
        """Get a notebook by name."""
        doc = self.storage.find_one(DB_COLLECTION, {"name": name})
        if not doc:
            return None
        return self._doc_to_notebook(doc)

    def list_notebooks(
        self,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[Notebook]:
        """List notebooks with optional tag filter."""
        filter_dict: dict[str, Any] = {}
        if tags:
            filter_dict["tags"] = tags

        docs = self.storage.find(DB_COLLECTION, filter_dict, limit=limit)
        return [self._doc_to_notebook(doc) for doc in docs]

    def update_notebook(
        self, notebook_id: str, updates: dict[str, Any]
    ) -> Notebook | None:
        """Update a notebook."""
        existing = self.get_notebook(notebook_id)
        if not existing:
            return None

        updates["updated_at"] = datetime.utcnow().isoformat()
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": notebook_id},
            updates,
        )
        return self.get_notebook(notebook_id)

    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook."""
        result = self.storage.delete_by_id(DB_COLLECTION, notebook_id)
        return result is not None

    def save_run(self, run: NotebookRun) -> NotebookRun:
        """Save a notebook run."""
        run_dict = run.model_dump()
        run_dict["started_at"] = run_dict["started_at"].isoformat()
        if run_dict["completed_at"]:
            run_dict["completed_at"] = run_dict["completed_at"].isoformat()

        self.storage.insert_one(RUNS_COLLECTION, run_dict)
        return run

    def get_runs(self, notebook_id: str, limit: int = 10) -> list[NotebookRun]:
        """Get runs for a notebook."""
        docs = self.storage.find(
            RUNS_COLLECTION,
            {"notebook_id": notebook_id},
            limit=limit,
        )
        return [self._doc_to_run(doc) for doc in docs]

    def _doc_to_notebook(self, doc: dict) -> Notebook:
        """Convert storage document to Notebook."""
        if isinstance(doc.get("created_at"), str):
            doc["created_at"] = datetime.fromisoformat(doc["created_at"])
        if isinstance(doc.get("updated_at"), str):
            doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
        return Notebook(**doc)

    def _doc_to_run(self, doc: dict) -> NotebookRun:
        """Convert storage document to NotebookRun."""
        if isinstance(doc.get("started_at"), str):
            doc["started_at"] = datetime.fromisoformat(doc["started_at"])
        if isinstance(doc.get("completed_at"), str):
            doc["completed_at"] = datetime.fromisoformat(doc["completed_at"])
        return NotebookRun(**doc)
