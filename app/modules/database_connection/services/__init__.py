from sqlalchemy import create_engine, inspect

from app.api.requests import DatabaseConnectionRequest
from app.api.responses import DatabaseConnectionResponse
from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.table_description.models import (
    TableDescription,
    TableDescriptionStatus,
)
from app.modules.table_description.repositories import TableDescriptionRepository


class DatabaseConnectionService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        database_connection = DatabaseConnection(
            alias=request.alias,
            connection_uri=request.connection_uri.strip(),
            schemas=request.schemas,
            metadata=request.metadata,
        )

        schemas_and_tables = {}

        if database_connection.schemas:
            for schema in database_connection.schemas:
                database_uri = f"{database_connection.connection_uri}?options=-csearch_path={schema}"
                engine = create_engine(database_uri)
                inspector = inspect(engine)
                tables = inspector.get_table_names() + inspector.get_view_names()
                if len(tables) == 0:
                    raise Exception("The db is empty")
                schemas_and_tables[schema] = [table.lower() for table in tables]

        # Connect db
        database_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = database_connection_repository.insert(database_connection)

        scanner_repository = TableDescriptionRepository(self.storage)
        # Add created tables
        for schema, tables in schemas_and_tables.items():
            for table in tables:
                table_description = TableDescription(
                    db_connection_id=db_connection.id,
                    db_schema=schema,
                    table_name=table,
                    sync_status=TableDescriptionStatus.NOT_SCANNED.value,
                )
                scanner_repository.save_table_info(table_description)

        return DatabaseConnectionResponse(**db_connection.model_dump())

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connections = db_connection_repository.find_all()
        return [
            DatabaseConnectionResponse(**db_connection.model_dump())
            for db_connection in db_connections
        ]

    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return None
