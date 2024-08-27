from app.data.db.storage import Storage
from app.modules.sql_generation.models import SQLGeneration

DB_COLLECTION = "sql_generations"


class SQLGenerationRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, sql_generation: SQLGeneration) -> SQLGeneration:
        sql_generation_dict = sql_generation.model_dump(exclude={"id"})
        sql_generation_dict["prompt_id"] = str(sql_generation.prompt_id)
        sql_generation.id = str(
            self.storage.insert_one(DB_COLLECTION, sql_generation_dict)
        )
        return sql_generation

    def update(self, sql_generation: SQLGeneration) -> SQLGeneration:
        sql_generation_dict = sql_generation.model_dump(exclude={"id"})
        sql_generation_dict["prompt_id"] = str(sql_generation.prompt_id)
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": sql_generation.id},
            sql_generation_dict,
        )
        return sql_generation

    def find_one(self, filter: dict) -> SQLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, filter)
        if not row:
            return None
        return SQLGeneration(**row)

    def find_by_id(self, id: str) -> SQLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return SQLGeneration(**row)

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[SQLGeneration]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(SQLGeneration(**row))
        return result
