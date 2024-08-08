from pydantic import BaseModel, Field


class DatabaseConnectionRequest(BaseModel):
    id: str
    alias: str | None = None
    dialect: str
    connection_uri: str
    schemas: list[str] | None = ["public"]
    metadata: dict | None = Field(default_factory=dict)
