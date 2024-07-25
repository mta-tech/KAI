from typing import List, Optional
from pydantic import BaseModel


class InstructionID(BaseModel):
    instruction_id: str


class InstructionList(BaseModel):
    db_connection_id: str
    page: Optional[int] = 1
    limit: Optional[int] = 10