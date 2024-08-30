from app.modules.instruction.models import Instruction

DB_COLLECTION = "instructions"

class InstructionRepository:
    def __init__(self, storage):
        self.storage = storage
    
    def insert(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.model_dump(exclude={"id"})
        instruction.id = str(self.storage.insert_one(DB_COLLECTION, instruction_dict))
        return instruction

    def find_by(self, filter: dict, page: int = 0, limit: int = 0) -> list[Instruction]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(Instruction(**row))
        return result

    def find_by_id(self, id: str) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return Instruction(**row)

    def find_all(self) -> list[Instruction]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = [Instruction(**row) for row in rows]
        return result
    
    def delete_by_id(self, id: str) -> bool:
        deleted_count = self.storage.delete_by_id(DB_COLLECTION, id)
        return deleted_count > 0 

    def update(self, instruction: Instruction) -> Instruction:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": instruction.id},
            instruction.model_dump(exclude={"id"}),
        )
        return instruction