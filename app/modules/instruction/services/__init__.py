from fastapi import HTTPException

from app.api.requests import InstructionRequest, UpdateInstructionRequest

# from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.instruction.models import Instruction
from app.modules.instruction.repositories import InstructionRepository
from app.modules.prompt.models import Prompt
from app.utils.model.embedding_model import EmbeddingModel


class InstructionService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = InstructionRepository(self.storage)

    def create_instruction(
        self, instruction_request: InstructionRequest
    ) -> Instruction:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            instruction_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(
                f"Database connection {instruction_request.db_connection_id} not found"
            )

        if not instruction_request.is_default:
            instruction_embedding = self.get_embedding(
                instruction_request.condition, instruction_request.rules
            )

        instruction = Instruction(
            db_connection_id=instruction_request.db_connection_id,
            condition=instruction_request.condition,
            rules=instruction_request.rules,
            instruction_embedding=instruction_embedding,
            is_default=instruction_request.is_default,
            metadata=instruction_request.metadata,
        )
        return self.repository.insert(instruction)

    def get_instruction(self, instruction_id) -> Instruction:
        instruction = self.repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(f"Prompt {instruction_id} not found")
        return instruction

    def get_instructions(self, db_connection_id) -> list[Instruction]:
        filter = {"db_connection_id": db_connection_id}
        return self.repository.find_by(filter)

    def retrieve_instruction_for_question(self, prompt: Prompt) -> list:
        default_filter = {
            "db_connection_id": prompt.db_connection_id,
            "is_default": 'true',
        }
        default_instructions = self.repository.find_by(default_filter)

        embedding_model = EmbeddingModel().get_model(
            model_family="openai", model_name="text-embedding-3-small"
        )
        prompt_embedding = embedding_model.embed_query(prompt.text)
        relevant_instructions = self.repository.find_by_relevance(
            prompt.db_connection_id, prompt.text, prompt_embedding
        )

        instructions = default_instructions + relevant_instructions

        return [
            {"instruction": f"{instruction.condition}, {instruction.rules}"}
            for instruction in instructions
        ]

    def update_instruction(
        self, instruction_id, update_request: UpdateInstructionRequest
    ) -> Instruction:
        instruction = self.repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(f"Instruction {instruction_id} not found")

        if update_request.condition is not None:
            instruction.condition = update_request.condition
            instruction.instruction_embedding = self.get_embedding(
                update_request.condition
            )
        if update_request.rules is not None:
            instruction.rules = update_request.rules
        if update_request.is_default is not None:
            instruction.is_default = update_request.is_default
        if update_request.metadata is not None:
            instruction.metadata = update_request.metadata

        return self.repository.update(instruction)

    def delete_instruction(self, instruction_id) -> bool:
        instruction = self.repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(f"Prompt {instruction_id} not found")

        is_deleted = self.repository.delete_by_id(instruction_id)

        if not is_deleted:
            raise HTTPException(f"Failed to delete instruction {instruction_id}")

        return True

    def get_embedding(self, condition, rules) -> list[float] | None:
        embedding_model = EmbeddingModel().get_model(
            model_family="openai", model_name="text-embedding-3-small"
        )

        instruction_embedding = embedding_model.embed_query(f"{condition}, {rules}")
        return instruction_embedding
