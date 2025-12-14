from datetime import datetime

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    id: str | None = None
    text: str
    db_connection_id: str
    schemas: list[str] | None = None
    context: list[dict] | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None
    # Original query text for Typesense searches (without conversation context)
    # If not set, falls back to 'text'
    search_text: str | None = None

    def get_search_text(self) -> str:
        """Get the text to use for Typesense searches."""
        return self.search_text if self.search_text else self.text
