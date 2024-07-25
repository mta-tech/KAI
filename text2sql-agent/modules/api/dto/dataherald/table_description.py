from typing import List, Optional
from pydantic import BaseModel


class TableDescriptionScan(BaseModel):
    ids: list
    metadata: Optional[dict] = {} 


class TableDescriptionID(BaseModel):
    table_decription_id: str


class TableDescriptionList(BaseModel):
    db_connection_id: str
    table_name: Optional[str] = None