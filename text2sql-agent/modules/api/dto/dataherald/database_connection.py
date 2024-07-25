from typing import Optional
from pydantic import BaseModel


class DBConnectionID(BaseModel):
    db_connection_id: str