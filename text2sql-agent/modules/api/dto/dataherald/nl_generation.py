from typing import List, Optional
from pydantic import BaseModel
from api.dto.dataherald.base_class import BaseLLMConfig, BaseSQLGeneration, BaseNLGeneration, BasePrompt


class NLGenerationID(BaseModel):
    nl_generation_id: str


class NLGenerationFromSQL(BaseLLMConfig, BaseSQLGeneration, BaseNLGeneration):
    pass


class NLGenerationFromPrompt(BaseLLMConfig, BaseSQLGeneration, BaseNLGeneration, BasePrompt):
    pass