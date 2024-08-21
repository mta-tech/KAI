import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SupportedDialects(Enum):
    POSTGRES = "postgresql"


class DatabaseConnection(BaseModel):
    id: str | None
    alias: str
    dialect: SupportedDialects | None
    connection_uri: str | None
    schemas: list[str] | None
    metadata: dict | None
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def get_dialect(cls, input_string):
        pattern = r"([^:/]+)://"
        match = re.match(pattern, input_string)
        if not match:
            raise ValueError(f"Invalid URI format: {input_string}")
        return match.group(1)

    @classmethod
    def set_dialect(cls, input_string):
        for dialect in SupportedDialects:
            if dialect.value in input_string:
                return dialect.value
        return None
