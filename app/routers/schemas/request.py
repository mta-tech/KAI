from typing import Dict, List, Optional

from pydantic import BaseModel


class DatabaseConnectionRequest(BaseModel):
    alias: str
    connection_uri: str
    schemas: Optional[List[str]] = []
    metadata: Optional[Dict] = {}
