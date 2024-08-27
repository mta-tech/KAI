from app.api.requests import PromptRequest, UpdateMetadataRequest
from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.prompt.models import Prompt
from app.modules.prompt.repositories import PromptRepository


class PromptService:
    def __init__(self, storage):
        self.storage = storage
        self.prompt_repository = PromptRepository(self.storage)

    def create_prompt(self, prompt_request: PromptRequest) -> Prompt:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            prompt_request.db_connection_id
        )
        if not db_connection:
            raise Exception(
                f"Database connection {prompt_request.db_connection_id} not found"
            )

        if not db_connection.schemas and prompt_request.schemas:
            raise Exception(
                "Schema not supported for this db",
                description=f"The {db_connection.dialect} dialect doesn't support schemas",
            )

        prompt = Prompt(
            text=prompt_request.text,
            db_connection_id=prompt_request.db_connection_id,
            schemas=prompt_request.schemas,
            metadata=prompt_request.metadata,
        )
        return self.prompt_repository.insert(prompt)

    def get_prompt(self, prompt_id) -> Prompt:
        prompt = self.prompt_repository.find_by_id(prompt_id)
        if not prompt:
            raise Exception(f"Prompt {prompt_id} not found")
        return prompt

    def update_prompt(
        self, prompt_id, metadata_request: UpdateMetadataRequest
    ) -> Prompt:
        prompt = self.prompt_repository.find_by_id(prompt_id)
        if not prompt:
            raise Exception(f"Prompt {prompt_id} not found")
        prompt.metadata = metadata_request.metadata
        return self.prompt_repository.update(prompt)

    def get_prompts(self, db_connection_id) -> list[Prompt]:
        filter = {"db_connection_id": db_connection_id}
        return self.prompt_repository.find_by(filter)
