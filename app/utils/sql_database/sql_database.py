"""SQL wrapper around SQLDatabase in langchain."""

import logging
import re
from typing import List
from urllib.parse import unquote
import os
import requests
import pandas as pd
from io import StringIO
from urllib.parse import urlparse

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

    @staticmethod
    def _dispose_engine_if_exists(db_id: str):
        if db_id in DBConnections.db_connections:
            try:
                sql_database_instance = DBConnections.db_connections[db_id]
                sql_database_instance.engine.dispose()
                del DBConnections.db_connections[db_id]
                logger.info(f"Disposed of engine for DB ID: {db_id}")
            except Exception as e:
                logger.error(f"Error disposing of engine for DB ID {db_id}: {e}")

    @staticmethod
    def dispose_all_engines():
        for db_id in list(
            DBConnections.db_connections.keys()
        ):  # Iterate over a copy of keys
            DBConnections._dispose_engine_if_exists(db_id)


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
        _engine_args = {
            "pool_size": 10,  # Maximum number of connections to keep in the pool
            "max_overflow": 5,  # Allow up to 10 connections to be created when pool is full
            "pool_timeout": 30,  # Timeout for getting connection from pool (seconds)
            "pool_recycle": 1500,  # Recycle connections after 1 hour
            "pool_pre_ping": True,  # Verify connections before use
        }

        # Configure SSL for Neon Database connections
        if database_uri.startswith("postgresql") and (
            "neon.tech" in database_uri.lower()
        ):
            _engine_args["connect_args"] = {
                "sslmode": "require"  # Enforce SSL connection for Neon
            }
        elif database_uri.startswith("postgresql"):
            _engine_args["connect_args"] = {
                "sslmode": "prefer"  # Try SSL first, fallback to non-SSL for local connections
            }

        if database_uri.lower().startswith("duckdb"):
            config = {"autoload_known_extensions": False}
            _engine_args["connect_args"] = {"config": config}

        if database_uri.lower().startswith("csv"):
            csv_path = database_uri.replace("csv://", "").strip()
            parsed_url = urlparse(csv_path)

            # Determine table name
            if parsed_url.scheme in ("http", "https"):
                response = requests.get(csv_path)
                response.raise_for_status()  # Ensure request success
                csv_data = StringIO(
                    response.text
                )  # Convert response text to file-like object
                table_name = os.path.basename(parsed_url.path).split(".")[0]
            else:
                table_name = os.path.basename(csv_path).split(".")[0]
                csv_data = csv_path  # Local file path

            table_name = re.sub(r"[^\w]", "_", table_name)
            df = pd.read_csv(csv_data, engine="pyarrow")

            # Create an **in-memory** SQLite database
            _engine_args.pop("max_overflow", None)
            _engine_args.pop("pool_timeout", None)
            _engine_args.pop("pool_pre_ping", None)

            engine = create_engine("sqlite:///:memory:", **_engine_args)

            # Store DataFrame into SQLite
            with engine.connect() as conn:
                df.to_sql(
                    table_name,
                    con=conn,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=1000,
                )

            return cls(engine)

        engine = create_engine(database_uri, **_engine_args)
        return cls(engine)

    @classmethod
    def get_sql_engine(
        cls, database_info: DatabaseConnection, refresh_connection=False
    ) -> "SQLDatabase":
        logger.info(f"Connecting db: {database_info.id}")
        existing_connection = DBConnections.db_connections

        # Case 1: Attempt to reuse an existing connection if not refreshing
        if database_info.id in existing_connection and not refresh_connection:
            try:
                sql_database = existing_connection[database_info.id]
                sql_database.engine.connect()  # Test if the connection is still valid
                return sql_database
            except Exception as e:
                logger.warning(
                    f"Existing connection for {database_info.id} is stale or invalid: {e}. Disposing and reconnecting."
                )
                DBConnections._dispose_engine_if_exists(database_info.id)

        # Case 2: Create a new connection (either no existing, or existing was stale/refresh_connection is True)
        # Ensure any old engine is disposed of before creating a new one,
        # especially if refresh_connection was True and the old one wasn't caught by the above try-except.
        DBConnections._dispose_engine_if_exists(database_info.id)

        fernet_encrypt = FernetEncrypt()
        try:
            db_uri = unquote(fernet_encrypt.decrypt(database_info.connection_uri))
            engine = cls.from_uri(db_uri)
            engine.engine.connect()
            DBConnections.add(database_info.id, engine)
            return engine
        except Exception as e:
            raise HTTPException(
                404,
                f"Unable to connect to db: {database_info.alias} {str(e)}",
            )

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

        def serialize_row(result: list) -> dict:
            # Handle duplicate field names
            unique_fields = []
            counter = {}

            for field in result[0]._fields:
                if field in counter:
                    counter[field] += 1
                    unique_fields.append(f"{field}{counter[field]}")
                else:
                    counter[field] = 1
                    unique_fields.append(field)

            return [dict(zip(unique_fields, values)) for values in result]

        with self._engine.connect() as connection:
            command = self.parser_to_filter_commands(command)
            cursor = connection.execute(text(command))
            if cursor.returns_rows and top_k:
                result = cursor.fetchmany(top_k)
                serialized_result = serialize_row(result)
                return str(serialized_result), {"result": serialized_result}
            if cursor.returns_rows:
                result = cursor.fetchall()
                serialized_result = serialize_row(result)
                return str(serialized_result), {"result": serialized_result}
        return "", {}

    def get_tables_and_views(self, schema=None) -> List[str]:
        inspector = inspect(self._engine)
        meta = MetaData()
        meta.reflect(bind=self._engine, views=True, schema=schema)
        rows = inspector.get_table_names(schema=schema) + inspector.get_view_names(
            schema=schema
        )
        if len(rows) == 0:
            raise Exception("The db is empty it could be a permission issue")
        return [row for row in rows]

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return self._engine.dialect.name
