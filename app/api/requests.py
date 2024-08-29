from pydantic import BaseModel, field_validator
from sql_metadata import Parser

from app.modules.sql_generation.models import LLMConfig


class DatabaseConnectionRequest(BaseModel):
    alias: str
    connection_uri: str
    schemas: list[str] | None = None
    metadata: dict | None = None


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str | None
    is_primary_key: bool | None
    data_type: str | None
    low_cardinality: bool | None
    categories: list[str] | None
    foreign_key: ForeignKeyDetail | None


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None
    metadata: dict | None = None


class ScannerRequest(BaseModel):
    table_description_ids: list[str] | None
    metadata: dict | None = None


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    schemas: list[str] | None = None
    metadata: dict | None = None


class SQLGenerationRequest(BaseModel):
    llm_config: LLMConfig | None
    evaluate: bool = False
    sql: str | None
    metadata: dict | None

    @field_validator("sql")
    @classmethod
    def validate_model_name(cls, v: str | None):
        try:
            Parser(v).tables  # noqa: B018
        except Exception as e:
            raise ValueError(f"SQL {v} is malformed. Please check the syntax.") from e
        return v


class PromptSQLGenerationRequest(SQLGenerationRequest):
    prompt: PromptRequest


class NLGenerationRequest(BaseModel):
    llm_config: LLMConfig | None
    max_rows: int = 100
    metadata: dict | None


class NLGenerationsSQLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLGenerationNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class UpdateMetadataRequest(BaseModel):
    metadata: dict | None
