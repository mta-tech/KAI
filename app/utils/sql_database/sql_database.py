"""SQL wrapper around SQLDatabase in langchain."""

import logging
import re
from typing import List
from urllib.parse import unquote

from fastapi import HTTPException
import sqlparse
from sqlalchemy import MetaData, create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import OperationalError

from app.modules.database_connection.models import DatabaseConnection
from app.utils.core.encrypt import FernetEncrypt

logger = logging.getLogger(__name__)


class DBConnections:
    db_connections = {}

    @staticmethod
    def add(uri, engine):
        DBConnections.db_connections[uri] = engine


class SQLDatabase:
    def __init__(self, engine: Engine):
        """Create engine from database URI."""
        self._engine = engine

    @property
    def engine(self) -> Engine:
        """Return SQL Alchemy engine."""
        return self._engine

    @classmethod
    def from_uri(cls, database_uri: str) -> "SQLDatabase":
        """Construct a SQLAlchemy engine from URI."""
        _engine_args = {}
        if database_uri.lower().startswith("duckdb"):
            config = {"autoload_known_extensions": False}
            _engine_args["connect_args"] = {"config": config}
        engine = create_engine(database_uri, **_engine_args)
        return cls(engine)

    @classmethod
    def get_sql_engine(
        cls, database_info: DatabaseConnection, refresh_connection=False
    ) -> "SQLDatabase":
        logger.info(f"Connecting db: {database_info.id}")
        try:
            existing_connection = DBConnections.db_connections
            if (
                database_info.id
                and database_info.id in existing_connection
                and not refresh_connection
            ):
                sql_database = DBConnections.db_connections[database_info.id]
                sql_database.engine.connect()
                return sql_database
        except OperationalError:
            pass

        fernet_encrypt = FernetEncrypt()
        try:
            db_uri = unquote(fernet_encrypt.decrypt(database_info.connection_uri))

            engine = cls.from_uri(db_uri)
            engine.engine.connect()
            DBConnections.add(database_info.id, engine)
        except Exception as e:
            raise HTTPException(404,   # noqa: B904
                f"Unable to connect to db: {database_info.alias} {str(e)}"
            )
        return engine

    @classmethod
    def extract_parameters(cls, input_string):
        # Define a regex pattern to extract the required parameters
        pattern = r"([^:/]+)://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^/]+)"

        # Use the regex pattern to match and extract the parameters
        match = re.match(pattern, input_string)

        if match:
            driver = match.group(1)
            user = match.group(2)
            password = match.group(3)
            host = match.group(4)
            port = match.group(5)
            db = match.group(6) if match.group(6) else None

            # Create a dictionary with the extracted parameters
            return {
                "driver": driver,
                "user": user,
                "password": password,
                "host": host,
                "port": port if port else None,
                "db": db,
            }

        return None

    @classmethod
    def parser_to_filter_commands(cls, command: str) -> str:
        sensitive_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "GRANT",
            "REVOKE",
            "ALTER",
            "TRUNCATE",
            "MERGE",
            "EXECUTE",
            "CREATE",
        ]
        parsed_command = sqlparse.parse(command)

        for stmt in parsed_command:
            for token in stmt.tokens:
                if (
                    isinstance(token, sqlparse.sql.Token)
                    and token.normalized in sensitive_keywords
                ):
                    raise HTTPException(
                        f"Sensitive SQL keyword '{token.normalized}' detected in the query."
                    )

        return command

    def run_sql(self, command: str, top_k: int = None) -> tuple[str, dict]:
        """Execute a SQL statement and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """

        def serialize_row(row: Row) -> dict:
            return dict(row._mapping)

        with self._engine.connect() as connection:
            command = self.parser_to_filter_commands(command)
            cursor = connection.execute(text(command))
            if cursor.returns_rows and top_k:
                result = cursor.fetchmany(top_k)
                serialized_result = [serialize_row(row) for row in result]
                return str(serialized_result), {"result": serialized_result}
            if cursor.returns_rows:
                result = cursor.fetchall()
                serialized_result = [serialize_row(row) for row in result]
                return str(serialized_result), {"result": serialized_result}
        return "", {}

    def get_tables_and_views(self) -> List[str]:
        inspector = inspect(self._engine)
        meta = MetaData()
        meta.reflect(bind=self._engine, views=True)
        rows = inspector.get_table_names() + inspector.get_view_names()
        if len(rows) == 0:
            raise Exception("The db is empty it could be a permission issue")
        return [row.lower() for row in rows]

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return self._engine.dialect.name
