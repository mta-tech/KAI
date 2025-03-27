from app.data.db.storage import Storage
from app.modules.alias.models import Alias

DB_COLLECTION = "aliases"


class AliasRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, alias: Alias) -> Alias:
        alias_dict = alias.model_dump(exclude={"id"})
        alias.id = str(self.storage.insert_one(DB_COLLECTION, alias_dict))
        return alias

    def find_by(self, filter: dict, page: int = 0, limit: int = 0) -> list[Alias]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(Alias(**row))
        return result

    def find_by_name(self, name: str, db_connection_id: str = None) -> Alias | None:
        if db_connection_id:
            # Use full text search with db_connection_id filter
            results = self.storage.full_text_search_by_db_connection_id(
                DB_COLLECTION,
                db_connection_id,
                name,
                ["name"]
            )
            if results and len(results) > 0:
                return Alias(**results[0])
            return None
        else:
            # Fallback to exact match if no db_connection_id provided
            filter = {"name": name}
            row = self.storage.find_exactly_one(
                DB_COLLECTION,
                filter,
            )
            if not row:
                return None
            return Alias(**row)

    def find_by_id(self, id: str) -> Alias | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return Alias(**row)

    def find_all(self) -> list[Alias]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = [Alias(**row) for row in rows]
        return result

    def delete_by_id(self, id: str) -> Alias | None:
        docs = self.storage.delete_by_id(DB_COLLECTION, id)
        return Alias(**docs) if docs else None

    def update(self, id: str, alias: Alias) -> Alias:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": id},
            alias.model_dump(exclude={"id"}),
        )
        return alias
