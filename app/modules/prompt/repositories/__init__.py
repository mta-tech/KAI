from app.modules.prompt.models import Prompt

DB_COLLECTION = "prompts"


class PromptRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, prompt: Prompt) -> Prompt:
        prompt_dict = prompt.model_dump(exclude={"id"})
        prompt.id = str(self.storage.insert_one(DB_COLLECTION, prompt_dict))
        return prompt

    def find_one(self, filter: dict) -> Prompt | None:
        row = self.storage.find_one(DB_COLLECTION, filter)
        if not row:
            return None
        return Prompt(**row)

    def find_by_id(self, id: str) -> Prompt | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return Prompt(**row)

    def find_by(self, filter: dict, page: int = 0, limit: int = 0) -> list[Prompt]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(Prompt(**row))
        return result

    def update(self, prompt: Prompt) -> Prompt:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": prompt.id},
            prompt.model_dump(exclude={"id"}),
        )
        return prompt
