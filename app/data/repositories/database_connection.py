from app.data import Storage
from app.data.models import DatabaseConnection
from app.data.repositories import Repository


class DatabaseConnectionRepository(Repository):
    def __init__(self, storage: Storage):
        super().__init__(storage)

    def list_database_connections(self) -> list[DatabaseConnection]:
        self.storage.search_document("database-connection", {})
        return self.storage.list_database_connections()
