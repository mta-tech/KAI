from pydantic import BaseModel, Field

from app.modules.database_connection.models import DatabaseConnection
from app.modules.sql_generation.models import IntermediateStep, LLMConfig
from app.modules.table_description.models import TableDescription
from app.modules.synthetic_questions.models import QuestionSQLPair


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
    prompt_text: str
    prompt_text_ner: str
    labels: list[str]
    entities: list[str]
    sql: str


class SQLGenerationResponse(BaseResponse):
    prompt_id: str
    status: str
    llm_config: LLMConfig | None
    intermediate_steps: list[IntermediateStep] | None
    sql: str | None
    input_tokens_used: int | None
    output_tokens_used: int | None
    confidence_score: float | None
    completed_at: str | None
    error: str | None

class NLGenerationResponse(BaseResponse):
    sql_generation_id: str
    llm_config: LLMConfig | None
    text: str | None
      
class DocumentResponse(BaseResponse):
    title: str | None = None
    content_type: str
    document_size: int
    text_content: str | None = None

class SyntheticQuestionResponse(BaseModel):
    questions: list[QuestionSQLPair]
    input_tokens_used: int | None
    output_tokens_used: int | None
    metadata: dict | None = None

class AliasResponse(BaseResponse):
    db_connection_id: str
    name: str
    target_name: str
    target_type: str
    description: str | None = None

class RetrieveKnowledgeResponse(BaseModel):
    final_answer: str=Field(alias="Final Answer")
    input_tokens_used: int
    output_tokens_used: int


class InsightResponse(BaseModel):
    """A single insight from analysis."""

    title: str
    description: str
    significance: str
    data_points: list[dict] | None = None


class ChartRecommendationResponse(BaseModel):
    """A chart recommendation from analysis."""

    chart_type: str
    title: str
    description: str
    x_axis: str | None = None
    y_axis: str | None = None
    columns: list[str] | None = None
    rationale: str | None = None


class AnalysisResponse(BaseResponse):
    """Response for analysis of SQL results."""

    sql_generation_id: str
    prompt_id: str | None = None
    summary: str
    insights: list[InsightResponse] = Field(default_factory=list)
    chart_recommendations: list[ChartRecommendationResponse] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    llm_config: LLMConfig | None = None
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    completed_at: str | None = None
    error: str | None = None


class ComprehensiveAnalysisResponse(BaseModel):
    """Response for end-to-end comprehensive analysis."""

    prompt_id: str
    sql_generation_id: str
    analysis_id: str | None = None
    sql: str | None = None
    sql_status: str
    summary: str
    insights: list[dict] = Field(default_factory=list)
    chart_recommendations: list[dict] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    error: str | None = None
    execution_time: dict = Field(default_factory=dict)