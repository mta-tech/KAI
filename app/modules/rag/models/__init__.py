from datetime import datetime

from pydantic import BaseModel, Field


class DocumentStore(BaseModel):
    id: str | None = None
    title: str | None = None
    content_type: str
    document_size: int
    text_content: str | None = None
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class RetrieveKnowledge(BaseModel):
    final_answer: str
    input_tokens_used: int
    output_tokens_used: int