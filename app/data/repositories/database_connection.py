from app.data import Storage
from app.data.models import DatabaseConnection
from app.data.repositories import Repository


class DatabaseConnectionRepository(Repository):
    def __init__(self, storage: Storage):
        super().__init__(storage)
        self.collection_name = "database_connection"

    def create_database_connection(
        self, database_connection: DatabaseConnection
    ) -> DatabaseConnection:
        document = database_connection.model_dump()
        created_document_data = self.storage.index_document(
            self.collection_name, document
        )
        created_document = DatabaseConnection(**created_document_data)

        return created_document

    def list_database_connections(self) -> list[DatabaseConnection]:
        results = self.storage.search_document(self.collection_name, {})
        print(results)
        database_connections = [DatabaseConnection(**db) for db in results]
        return database_connections
