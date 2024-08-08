from datetime import datetime
from pydantic import BaseModel, BaseSettings, Extra, Field, validator
from enum import Enum


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
            raise InvalidURIFormatError(f"Invalid URI format: {input_string}")
        return match.group(1)

    @classmethod
    def set_dialect(cls, input_string):
        for dialect in SupportedDialects:
            if dialect.value in input_string:
                return dialect.value
        return None

    @validator("connection_uri", pre=True, always=True)
    def connection_uri_format(cls, value: str, values):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
        except Exception:
            dialect_prefix = cls.get_dialect(value)
            values["dialect"] = cls.set_dialect(dialect_prefix)
            value = fernet_encrypt.encrypt(value)
        return value

    @validator("llm_api_key", pre=True, always=True)
    def llm_api_key_encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def decrypt_api_key(self):
        if self.llm_api_key is not None and self.llm_api_key != "":
            fernet_encrypt = FernetEncrypt()
            return fernet_encrypt.decrypt(self.llm_api_key)
        return os.environ.get("OPENAI_API_KEY")