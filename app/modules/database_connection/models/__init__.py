import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.utils.core.encrypt import FernetEncrypt


class SupportedDialects(Enum):
    POSTGRES = "postgresql"
    CSV = "csv"


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
    def set_dialect(cls, input_string) -> Optional[SupportedDialects]:
        for dialect in SupportedDialects:
            if dialect.value in input_string:
                return dialect.value
        return None

    @model_validator(mode="before")
    def connection_uri_format(cls, values):
        connection_uri = values.get("connection_uri")
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(connection_uri)
        except Exception:
            # if its encrypted dialect already setted
            dialect_prefix = cls.get_dialect(connection_uri)
            values["dialect"] = cls.set_dialect(dialect_prefix)
        return values

    @model_validator(mode="before")
    def set_default_schema(cls, values):
        schemas = values.get("schemas")
        if not schemas:
            values["schemas"] = ["public"]
        return values
