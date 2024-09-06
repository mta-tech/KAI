from pydantic import BaseModel

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
    is_default: bool


class ContextStoreResponse(BaseResponse):
    db_connection_id: str
    prompt: str
    sql: str


class SQLGenerationResponse(BaseResponse):
    prompt_id: str
    status: str
    llm_config: LLMConfig | None
    intermediate_steps: list[IntermediateStep] | None
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    completed_at: str | None
    error: str | None


class NLGenerationResponse(BaseResponse):
    sql_generation_id: str
    llm_config: LLMConfig | None
    text: str | None
