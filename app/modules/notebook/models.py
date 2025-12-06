"""Notebook data models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CellType(str, Enum):
    """Types of notebook cells."""

    QUERY = "query"
    VISUALIZATION = "visualization"
    TEXT = "text"
    CODE = "code"
    USER_INPUT = "user_input"


class CellStatus(str, Enum):
    """Execution status of a cell."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Parameter(BaseModel):
    """Notebook parameter definition."""

    name: str
    param_type: str = "text"
    default: Any = None
    description: str | None = None
    options: list[str] | None = None
    required: bool = False


class Cell(BaseModel):
    """A single cell in a notebook."""

    id: str
    cell_type: CellType
    name: str
    prompt: str | None = None
    code: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    output: Any = None
    status: CellStatus = CellStatus.PENDING
    error: str | None = None
    execution_time_ms: float | None = None


class Notebook(BaseModel):
    """A reusable analysis notebook."""

    id: str
    name: str
    description: str | None = None
    database_alias: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    cells: list[Cell] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotebookRun(BaseModel):
    """A single execution of a notebook."""

    id: str
    notebook_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    results: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    execution_time_ms: float | None = None


class NotebookCreateRequest(BaseModel):
    """Request to create a notebook."""

    name: str
    description: str | None = None
    database_alias: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    cells: list[Cell] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class NotebookRunRequest(BaseModel):
    """Request to run a notebook."""

    parameters: dict[str, Any] = Field(default_factory=dict)
    database_alias: str | None = None
