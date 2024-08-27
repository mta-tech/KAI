import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class SupportedDialects(Enum):
    POSTGRES = "postgresql"


class DatabaseConnection(BaseModel):
    id: Optional[str] = None
    alias: str
    dialect: str
    connection_uri: str
    schemas: list[str]
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def get_dialect(cls, input_string: str) -> str:
        pattern = r"([^:/]+)://"
        match = re.match(pattern, input_string)
        if not match:
            raise ValueError(f"Invalid URI format: {input_string}")
        return match.group(1)

    @classmethod
    def check_dialect(cls, input_string: str) -> Optional[SupportedDialects]:
        for dialect in SupportedDialects:
            if dialect.value in input_string:
                return dialect.value
        return None

    @model_validator(mode="before")
    def set_dialect(cls, values):
        connection_uri = values.get("connection_uri")
        if connection_uri:
            dialect_prefix = cls.get_dialect(connection_uri)
            dialect = cls.check_dialect(dialect_prefix)
            if dialect:
                values["dialect"] = dialect
        return values

    @model_validator(mode="before")
    def set_default_schema(cls, values):
        schemas = values.get("schemas")
        if not schemas:
            values["schemas"] = ["public"]
        return values
