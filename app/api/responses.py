from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.database_connection.models import DatabaseConnection
from app.modules.sql_generation.models import IntermediateStep, LLMConfig
from app.modules.table_description.models import TableDescription


class BaseResponse(BaseModel):
    id: str
    metadata: dict | None
    created_at: str | None


class DatabaseConnectionResponse(BaseResponse, DatabaseConnection):
    pass


class TableDescriptionResponse(BaseResponse, TableDescription):
    pass


class PromptResponse(BaseResponse):
    text: str
    db_connection_id: str
    schemas: list[str] | None


class BusinessGlossaryResponse(BaseResponse):
    db_connection_id: str
    metric: str
    alias: list[str] | None
    sql: str


class InstructionResponse(BaseResponse):
    db_connection_id: str
    condition: str
    rules: str
    condition_embedding: list[float] | None = None
    is_default: bool


class ContextStoreResponse(BaseResponse):
    db_connection_id: str
    prompt_text: str
    prompt_embedding: list[float] | None = None
    sql: str
    is_parameterized: bool
    parameterized_entity: dict | None = None #Stores NER (entity: type)
    

class SQLGenerationResponse(BaseResponse):
    id: str
    prompt_id: str
    status: str
    llm_config: LLMConfig | None
    intermediate_steps: list[IntermediateStep] | None
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    completed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    error: str | None


class DocumentResponse(BaseResponse):
    title: str | None = None
    content_type: str
    document_size: int
    text_content: str | None = None