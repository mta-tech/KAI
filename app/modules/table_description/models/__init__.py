from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TableDescriptionStatus(Enum):
    NOT_SCANNED = "NOT_SCANNED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SCANNED = "SCANNED"
    FAILED = "FAILED"


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDescription(BaseModel):
    name: str
    description: str | None = None
    is_primary_key: bool = False
    data_type: str = "str"
    low_cardinality: bool = False
    categories: list[Any] | None = None
    foreign_key: ForeignKeyDetail | None = None


class TableDescription(BaseModel):
    id: str | None = None
    db_connection_id: str
    db_schema: str
    table_name: str
    columns: list[ColumnDescription] = []
    examples: list = []
    table_description: str | None = None
    table_embedding: str | None = None
    table_schema: str | None = None
    sync_status: str = TableDescriptionStatus.SCANNED.value
    last_sync: str | None = None
    error_message: str | None = None
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
