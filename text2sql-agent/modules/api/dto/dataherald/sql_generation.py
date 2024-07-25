from typing import List, Optional
from pydantic import BaseModel
from api.dto.dataherald.base_class import BasePrompt, BaseSQLGeneration


class SQLGenerationID(BaseModel):
    sql_generation_id: str


class SQLGenerationPrompt(BasePrompt, BaseSQLGeneration):
    pass


class SQLGenerationExecute(BaseModel):
    sql_generation_id: str
    max_rows: Optional[int] = 100