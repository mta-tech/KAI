
from fastapi import HTTPException
from app.api.requests import InstructionRequest, UpdateInstructionRequest
# from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.instruction.models import Instruction
from app.modules.instruction.repositories import InstructionRepository


class InstructionService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = InstructionRepository(self.storage)

    def create_instruction(self, instruction_request: InstructionRequest) -> Instruction:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            instruction_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(
                f"Database connection {instruction_request.db_connection_id} not found"
            )

        # if not db_connection.schemas and prompt_request.schemas:
        #     raise HTTPException(
        #         "Schema not supported for this db",
        #         description=f"The {db_connection.dialect} dialect doesn't support schemas",
        #     )

        instruction = Instruction(
            db_connection_id=instruction_request.db_connection_id,
            condition=instruction_request.condition,
            rules=instruction_request.rules,
            condition_embedding= self.get_embedding(instruction_request.condition), 
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

    def update_instruction(
        self, instruction_id, update_request: UpdateInstructionRequest
    ) -> Instruction:
        instruction = self.repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(f"Instruction {instruction_id} not found")
        
        if update_request.condition is not None:
            instruction.condition = update_request.condition
            instruction.condition_embedding = self.get_embedding(update_request.condition)
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



# TODO Link to embedding module
    def get_embedding(self, text) -> list[float] | None:
        print(f'Run get_embedding on: {text}')
        return None