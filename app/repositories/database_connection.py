from app.repositories import DatabaseConnection
from app.storage.typesense import TypeSenseDB

class DatabaseConnectionRepository:
    def __init__(self):
        self.storage = TypeSenseDB()

    def list_database_connections(self) -> list[DatabaseConnection]:
        self.storage.search_document("database-connection", {})
        return self.storage.list_database_connections()