import re

from app.api.requests import DatabaseConnectionRequest
from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.table_description.repositories import TableDescriptionRepository
from app.utils.core.encrypt import FernetEncrypt
from app.utils.sql_database.sql_database import SQLDatabase


class DatabaseConnectionService:
    def __init__(self, scanner, storage: Storage):
        self.scanner = scanner
        self.storage = storage

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        database_connection = DatabaseConnection(
            alias=request.alias,
            connection_uri=request.connection_uri.strip(),
            schemas=request.schemas,
            metadata=request.metadata,
        )

        schemas_and_tables = {}
        fernet_encrypt = FernetEncrypt()

        if database_connection.schemas:
            for schema in database_connection.schemas:
                # Put Schema in database uri
                db_uri_with_schema = self.add_schema_in_uri(
                    request.connection_uri.strip(),
                    schema,
                    str(database_connection.dialect),
                )

                database_connection.connection_uri = fernet_encrypt.encrypt(
                    db_uri_with_schema
                )

                sql_database = SQLDatabase.get_sql_engine(database_connection, True)
                schemas_and_tables[schema] = sql_database.get_tables_and_views()

        # Connect db
        database_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection.connection_uri = fernet_encrypt.encrypt(
            self.remove_schema_in_uri(
                request.connection_uri.strip(),
                str(database_connection.dialect),
            )
        )
        db_connection = database_connection_repository.insert(database_connection)

        scanner_repository = TableDescriptionRepository(self.storage)
        # Add created tables
        for schema, tables in schemas_and_tables.items():
            self.scanner.create_tables(
                tables, str(db_connection.id), schema, scanner_repository
            )

        return DatabaseConnection(**db_connection.model_dump())

    def list_database_connections(self) -> list[DatabaseConnection]:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connections = db_connection_repository.find_all()
        return [
            DatabaseConnection(**db_connection.model_dump())
            for db_connection in db_connections
        ]

    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnection:
        return None

    def remove_schema_in_uri(self, connection_uri: str, dialect: str) -> str:
        if dialect in ["postgresql"]:
            pattern = r"\?options=-csearch_path" r"=[^&]*"
            return re.sub(pattern, "", connection_uri)
        return connection_uri

    def add_schema_in_uri(self, connection_uri: str, schema: str, dialect: str) -> str:
        if dialect in ["postgresql"]:
            return f"{connection_uri}?options=-csearch_path={schema}"
        return connection_uri

    def get_sql_database(
        self, database_connection: DatabaseConnection, schema: str = None
    ) -> SQLDatabase:
        fernet_encrypt = FernetEncrypt()
        if schema:
            database_connection.connection_uri = fernet_encrypt.encrypt(
                self.add_schema_in_uri(
                    fernet_encrypt.decrypt(database_connection.connection_uri),
                    schema,
                    database_connection.dialect,
                )
            )
        return SQLDatabase.get_sql_engine(database_connection, True)
