from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection

DB_COLLECTION = "database_connections"


class DatabaseConnectionRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, database_connection: DatabaseConnection) -> DatabaseConnection:
        doc = database_connection.model_dump(exclude={"id"})
        database_connection.id = str(self.storage.insert_one(DB_COLLECTION, doc))
        return database_connection

    def find_one(self, filter: dict) -> DatabaseConnection | None:
        doc = self.storage.find_one(DB_COLLECTION, filter)
        return DatabaseConnection(**doc) if doc else None

    def update(self, database_connection: DatabaseConnection) -> DatabaseConnection:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": database_connection.id},
            database_connection.model_dump(exclude={"id"}),
        )
        return database_connection

    def find_by_id(self, id: str) -> DatabaseConnection | None:
        doc = self.storage.find_one(DB_COLLECTION, {"id": id})
        return DatabaseConnection(**doc) if doc else None

    def find_all(self) -> list[DatabaseConnection]:
        docs = self.storage.find_all(DB_COLLECTION)
        result = []
        for doc in docs:
            obj = DatabaseConnection(**doc)
            result.append(obj)
        return result
    
    def delete_by_id(self, id: str) -> DatabaseConnection:
        doc = self.storage.delete_by_id(DB_COLLECTION, id)
        return DatabaseConnection(**doc) if doc else None
