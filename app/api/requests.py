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
    instruction: str | None
    llm_config: LLMConfig | None = None
    metadata: dict | None = None


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    schemas: list[str] | None = None
    context: list[dict] | None = None
    metadata: dict | None = None
    # Original query text for Typesense searches (without conversation context)
    # If not set, falls back to 'text'
    search_text: str | None = None


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


class GetContextStoreByNameRequest(BaseModel):
    db_connection_id: str
    prompt_text: str


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


class AliasRequest(BaseModel):
    db_connection_id: str
    name: str
    target_name: str
    target_type: str
    description: str | None = None
    metadata: dict | None = None


class UpdateAliasRequest(BaseModel):
    name: str | None = None
    target_name: str | None = None
    target_type: str | None = None
    description: str | None = None
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


class SyntheticQuestionRequest(BaseModel):
    db_connection_id: str
    llm_config: LLMConfig | None
    instruction: str | None
    questions_per_batch: int = 5
    num_batches: int = 1
    peeking_context_stores: bool = False
    evaluate: bool = False
    metadata: dict | None = None


class AnalysisRequest(BaseModel):
    """Request for generating analysis from an existing SQL generation."""

    llm_config: LLMConfig | None = None
    max_rows: int = 100
    metadata: dict | None = None


class ComprehensiveAnalysisRequest(BaseModel):
    """Request for end-to-end analysis: Prompt -> SQL Gen -> Execution -> Analysis."""

    prompt: PromptRequest
    llm_config: LLMConfig | None = None
    max_rows: int = 100
    use_deep_agent: bool = False
    metadata: dict | None = None
