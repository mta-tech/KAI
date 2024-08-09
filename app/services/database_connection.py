from sqlalchemy import create_engine, inspect

from app.data import Storage
from app.data.repositories.database_connection import DatabaseConnectionRepository
from app.server.config import Settings
from app.services import Service


class DatabaseConnectionService(Service):
    def __init__(self, settings: Settings, storage: Storage):
        super().__init__(settings, storage)
        self.repository = DatabaseConnectionRepository(self.storage)

    def list_database_connections():
        return ["list_database_connection"]

    def create_database_connection(db_url):
        engine = create_engine(db_url)
        inspector = inspect(engine)
        db_structure = {}

        tables = inspector.get_table_names()
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            db_structure[table_name] = [column["name"] for column in columns]

        for table, columns in db_structure.items():
            print(f"Table: {table}")
            for column in columns:
                print(f"  Column: {column}")

    def update_database_connections():
        return "update_database_connections"

    def delete_database_connections():
        return "delete_database_connections"
