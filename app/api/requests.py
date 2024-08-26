from pydantic import BaseModel


class DatabaseConnectionRequest(BaseModel):
    alias: str
    connection_uri: str
    schemas: list[str] | None = None
    metadata: dict | None = None


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str | None
    is_primary_key: bool | None
    data_type: str | None
    low_cardinality: bool | None
    categories: list[str] | None
    foreign_key: ForeignKeyDetail | None


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None
    metadata: dict | None = None

class ScannerRequest(BaseModel):
    table_description_ids: list[str] | None
    metadata: dict | None = None