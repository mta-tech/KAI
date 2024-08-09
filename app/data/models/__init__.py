from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.utils.constant import (
    SQLGenerationStatus,
    SupportedDatabase,
    TableDescriptionStatus,
)


class DatabaseConnection(BaseModel):
    id: str
    alias: str | None = None
    dialect: str
    connection_uri: str
    schemas: list[str] | None = ["public"]
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())

    @field_validator("dialect")
    def validate_dialect(cls, value):
        if value not in SupportedDatabase.__members__:
            raise ValueError(
                f"{value} is not a valid dialect. Supported values are: {list(SupportedDatabase.__members__.keys())}"
            )
        return value


class Prompt(BaseModel):
    id: str
    db_connection_id: str
    text: str
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())


class SQLGeneration(BaseModel):
    id: str
    prompt_id: str
    llm_name: str
    evaluate: bool = False
    evaluation_score: float | None
    status: str
    sql: str
    error_message: str | None = None
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())
    completed_at: datetime

    @field_validator("status")
    def validate_dialect(cls, value):
        if value not in SQLGenerationStatus.__members__:
            raise ValueError(f"{value} is not a valid sql generation status.")
        return value


class NLGeneration(BaseModel):
    id: str
    sql_generation_id: str
    llm_name: str
    text: str
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())


class DatabaseInstruction(BaseModel):
    id: str
    db_connection_id: str
    instruction: str
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())


class ContextStore(BaseModel):
    id: str
    db_connection_id: str
    prompt_text: str
    prompt_embedding: List[float]
    sql: str
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())


class TableDescription(BaseModel):
    id: str
    db_connection_id: str
    schema_name: str
    table_name: str
    table_embedding: List[float]
    description: str | None = None
    status: str
    table_schema: str
    error_message: str | None = None
    metadata: dict | None = Field(default_factory=dict)
    last_table_sync: datetime
    created_at: str = str(datetime.now())

    @field_validator("status")
    def validate_dialect(cls, value):
        if value not in TableDescriptionStatus.__members__:
            raise ValueError(
                f"{value} is not a valid table description status. Valid statuses are: {list(SupportedDatabase.__members__.keys())}"
            )
        return value


class ColumnDescription(BaseModel):
    id: str
    table_description_id: str
    name: str
    is_primary_key: bool = False
    data_type: str
    description: str | None = None
    low_cardinality: bool = False
    categories: str | None = None
    foreign_key: str | None = None
    examples: list[str] = Field(default_factory=list)
    metadata: dict | None = Field(default_factory=dict)
    created_at: str = str(datetime.now())
