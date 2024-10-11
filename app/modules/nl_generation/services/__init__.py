from datetime import datetime

from fastapi import HTTPException

from app.api.requests import (
    NLGenerationRequest,
    NLGenerationsSQLGenerationRequest,
    PromptSQLGenerationNLGenerationRequest,
)
from app.modules.nl_generation.models import LLMConfig, NLGeneration
from app.modules.nl_generation.repositories import NLGenerationRepository
from app.modules.prompt.models import Prompt
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.models import SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.sql_generation.services import SQLGenerationService
from app.utils.nl_generator.generates_nl_answer import GeneratesNlAnswer


class NLGenerationService:
    def __init__(self, storage):
        self.storage = storage
        self.nl_generation_repository = NLGenerationRepository(storage)

    def create_nl_generation(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGeneration:
        initial_nl_generation = NLGeneration(
            sql_generation_id=sql_generation_id,
            created_at=str(datetime.now()),
            llm_config=(
                nl_generation_request.llm_config
                if nl_generation_request.llm_config
                else LLMConfig()
            ),
            metadata=nl_generation_request.metadata,
        )
        self.nl_generation_repository.insert(initial_nl_generation)
        sql_generation_repository = SQLGenerationRepository(self.storage)
        sql_generation = sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise HTTPException(
                f"SQL Generation {sql_generation_id} not found",
                initial_nl_generation.id,
            )
        nl_generator = GeneratesNlAnswer(
            self.storage,
            (
                nl_generation_request.llm_config
                if nl_generation_request.llm_config
                else LLMConfig()
            ),
        )
        try:
            nl_generation = nl_generator.execute(
                sql_generation=sql_generation,
                top_k=nl_generation_request.max_rows,
            )
        except Exception as e:
            raise HTTPException(str(e), initial_nl_generation.id) from e
        initial_nl_generation.text = nl_generation.text
        return self.nl_generation_repository.update(initial_nl_generation)

    def create_sql_and_nl_generation(
        self,
        prompt_id: str,
        nl_generation_sql_generation_request: NLGenerationsSQLGenerationRequest,
    ) -> NLGeneration:
        sql_generation_service = SQLGenerationService(self.storage)
        sql_generation: SQLGeneration = sql_generation_service.create_sql_generation(
            prompt_id, nl_generation_sql_generation_request.sql_generation
        )

        nl_generation_request = NLGenerationRequest(
            **nl_generation_sql_generation_request.model_dump()
        )

        nl_generation = self.create_nl_generation(
            sql_generation.id, nl_generation_request
        )
        return NLGeneration(**nl_generation.model_dump())

    def create_prompt_sql_and_nl_generation(
        self, request: PromptSQLGenerationNLGenerationRequest
    ) -> NLGeneration:
        prompt_service = PromptService(self.storage)
        prompt: Prompt = prompt_service.create_prompt(request.sql_generation.prompt)
        sql_generation_service = SQLGenerationService(self.storage)
        sql_generation: SQLGeneration = sql_generation_service.create_sql_generation(
            prompt.id, request.sql_generation
        )

        nl_generation_request = NLGenerationRequest(**request.model_dump())
        nl_generation = self.create_nl_generation(sql_generation.id, nl_generation_request)
        return NLGeneration(**nl_generation.model_dump())

    def get_nl_generations(self, sql_generation_id: str) -> list[NLGeneration]:
        sql_generation_repository = SQLGenerationRepository(self.storage)
        sql_generation = sql_generation_repository.find_by_id(sql_generation_id)
        if sql_generation is None:
            raise HTTPException(
                status_code=404, detail=f"SQL Generation {sql_generation_id} not found"
            )
        nl_generations = self.nl_generation_repository.find_by(
            {"sql_generation_id": sql_generation_id}
        )
        return [
            NLGeneration(**nl_generation.model_dump())
            for nl_generation in nl_generations
        ]

    def update_nl_generation(self, nl_generation_id, metadata_request) -> NLGeneration:
        nl_generation = self.nl_generation_repository.find_by_id(nl_generation_id)
        if not nl_generation:
            raise HTTPException(f"NL generation {nl_generation_id} not found")
        nl_generation.metadata = metadata_request.metadata
        return self.nl_generation_repository.update(nl_generation)

    def get_nl_generation(self, nl_generation_id: str) -> NLGeneration:
        nl_generation = self.nl_generation_repository.find_by_id(nl_generation_id)
        if not nl_generation:
            raise HTTPException(404, f"NL Generation {nl_generation_id} not found")
        return nl_generation
