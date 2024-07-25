from typing import List, Optional
from pydantic import BaseModel


class PromptID(BaseModel):
    prompt_id: str