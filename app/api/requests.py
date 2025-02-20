from typing import Optional

from pydantic import BaseModel, field_validator
from sql_metadata import Parser

from app.modules.sql_generation.models import LLMConfig


class DatabaseConnectionRequest(BaseModel):
    alias: str
    connection_uri: str = "postgresql://<user>:<password>@<host>/<db-name>"
    schemas: list[str] | None = None
    metadata: dict | None = None


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str | None = None
    is_primary_key: bool | None = None
    data_type: str | None = None
    low_cardinality: bool | None = None
    categories: list[str] | None = None
    foreign_key: ForeignKeyDetail | None = None


class TableDescriptionRequest(BaseModel):
    table_description: str | None = None
    columns: list[ColumnDescriptionRequest] | None = None
    metadata: dict | None = None


class ScannerRequest(BaseModel):
    table_description_ids: list[str] | None
    llm_config: LLMConfig | None = None
    metadata: dict | None = None


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    schemas: list[str] | None = None
    context: list[dict] | None = None
    metadata: dict | None = None


class BusinessGlossaryRequest(BaseModel):
    metric: str
    alias: list[str] | None = None
    sql: str
    metadata: dict | None = None


class InstructionRequest(BaseModel):
    db_connection_id: str
    condition: str
    rules: str
    is_default: bool = False
    metadata: dict | None = None


class UpdateInstructionRequest(BaseModel):
    condition: Optional[str] = None
    rules: Optional[str] = None
    is_default: Optional[bool] = None
    metadata: Optional[dict] = None


class ContextStoreRequest(BaseModel):
    db_connection_id: str
    prompt_text: str
    sql: str
    metadata: dict | None = None

class SemanticContextStoreRequest(BaseModel):
    db_connection_id: str
    prompt_text: str
    top_k: int = 3


class UpdateContextStoreRequest(BaseModel):
    prompt_text: Optional[str] = None
    sql: Optional[str] = None
    metadata: Optional[dict] = None


class SQLGenerationRequest(BaseModel):
    llm_config: LLMConfig | None
    using_ner: bool = False
    evaluate: bool = False
    sql: str | None = None
    metadata: dict | None = None

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
    metadata: dict | None = None


class NLGenerationsSQLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLGenerationNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class UpdateBusinessGlossaryRequest(BaseModel):
    metric: str | None = None
    alias: list[str] | None = None
    sql: str | None = None
    metadata: dict | None = None


class UpdateMetadataRequest(BaseModel):
    metadata: dict | None


class TextRequest(BaseModel):
    title: str | None = "General Information"
    content_type: str | None = "text"
    text_content: str
    metadata: dict | None = None


class EmbeddingRequest(BaseModel):
    document_id: str
    title: str | None = None
    text_content: str
    metadata: dict | None = None
