from typing import List, Optional
from pydantic import BaseModel


class GoldenSQLID(BaseModel):
    golden_sql_id: str


class GoldenSQLList(BaseModel):
    db_connection_id: str
    page: Optional[int] = 1
    limit: Optional[int] = 10