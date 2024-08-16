import uuid
from datetime import datetime

from sqlalchemy import create_engine, inspect

from app.data import Storage
from app.data.models import DatabaseConnection
from app.data.repositories.database_connection import DatabaseConnectionRepository
from app.routers.schemas.request import DatabaseConnectionRequest
from app.services import Service


class DatabaseConnectionService(Service):
    def __init__(self, storage: Storage):
        super().__init__(storage)
        self.repository = DatabaseConnectionRepository(self.storage)

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        db_uri = request.connection_uri
        engine = create_engine(db_uri)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Valid Connection
        if len(tables) > 0:
            # Create Database Connection
            database_connection = DatabaseConnection(
                id=str(uuid.uuid4()),
                dialect='POSTGRES',
                **request.model_dump(),
                created_at=str(datetime.now()),
            )
            created_database_connetion = self.repository.create_database_connection(
                database_connection
            )
            # TODO: Create Table Description Not Scanned
            return created_database_connetion
        else:
            # Invalid Connection
            raise Exception("No tabels found in database")

    def list_database_connections(self):
        database_connections = self.repository.list_database_connections()
        return database_connections

    def update_database_connections():
        return "update_database_connections"

    def delete_database_connections():
        return "delete_database_connections"
