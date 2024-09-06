from app.data.db.storage import Storage
from app.modules.context_store.models import ContextStore

DB_COLLECTION = "context_stores"


class ContextStoreRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, context_store: ContextStore) -> ContextStore:
        context_store_dict = context_store.model_dump(exclude={"id"})
        context_store.id = str(
            self.storage.insert_one(DB_COLLECTION, context_store_dict)
        )
        return context_store

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[ContextStore]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(ContextStore(**row))
        return result

    def find_by_prompt(self, db_connection_id: str, prompt: str) -> ContextStore | None:
        row = self.storage.find_one(
            DB_COLLECTION, {"db_connection_id": db_connection_id, "prompt": prompt}
        )
        if not row:
            return None
        return ContextStore(**row)

    def find_by_id(self, id: str) -> ContextStore | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return ContextStore(**row)

    def find_all(self) -> list[ContextStore]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = [ContextStore(**row) for row in rows]
        return result

    def delete_by_id(self, id: str) -> bool:
        deleted_count = self.storage.delete_by_id(DB_COLLECTION, id)
        return deleted_count > 0

    def update(self, context_store: ContextStore) -> ContextStore:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": context_store.id},
            context_store.model_dump(exclude={"id"}),
        )
        return context_store
