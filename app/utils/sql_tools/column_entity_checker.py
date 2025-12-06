import difflib
import re
from typing import ClassVar, List, Pattern
from sqlalchemy import text

from fastapi import HTTPException
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError

from app.modules.table_description.models import TableDescription
from app.server.errors import sql_agent_exceptions
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_tools import replace_unprocessable_characters


class ColumnEntityChecker(BaseTool):
    """Tool for checking the existance of an entity inside a column."""

    name: str = "DbColumnEntityChecker"
    description: str = """
    Input: Column name and its corresponding table, and an entity.
    Output: cell-values found in the column similar to the given entity.
    Use this tool to get cell values similar to the given entity in the given column.

    Example Input: table1 -> column2, entity
    """
    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List[TableDescription]
    is_multiple_schema: bool

    # Valid identifier pattern: alphanumeric, underscores, dots (for schema.table)
    VALID_IDENTIFIER_PATTERN: ClassVar[Pattern[str]] = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$')

    def _validate_identifier(self, identifier: str) -> bool:
        """Validate that an identifier is safe for SQL queries."""
        return bool(self.VALID_IDENTIFIER_PATTERN.match(identifier))

    def _quote_identifier(self, identifier: str) -> str:
        """Quote an identifier to prevent SQL injection."""
        # Replace any double quotes with escaped double quotes
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    def find_similar_strings(
        self, input_list: List[tuple], target_string: str, threshold=0.4
    ):
        similar_strings = []
        for item in input_list:
            similarity = difflib.SequenceMatcher(
                None, str(item[0]).strip().lower(), target_string.lower()
            ).ratio()
            if similarity >= threshold:
                similar_strings.append((str(item[0]).strip(), similarity))
        similar_strings.sort(key=lambda x: x[1], reverse=True)
        return similar_strings[:25]

    @sql_agent_exceptions()
    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        try:
            schema, entity = tool_input.split(",")
            table_name, column_name = schema.split("->")
            table_name = replace_unprocessable_characters(table_name)
            column_name = replace_unprocessable_characters(column_name).strip()
            if "." not in table_name and self.is_multiple_schema:
                raise HTTPException(
                    "Table name should be in the format db_schema.table_name"
                )
        except ValueError:
            return "Invalid input format, use following format: table_name -> column_name, entity (entity should be a string without ',')"

        # Validate identifiers to prevent SQL injection
        if not self._validate_identifier(table_name):
            return f"Invalid table name: {table_name}. Only alphanumeric characters, underscores, and dots are allowed."
        if not self._validate_identifier(column_name):
            return f"Invalid column name: {column_name}. Only alphanumeric characters and underscores are allowed."

        # Quote identifiers for safe SQL construction
        quoted_table = self._quote_identifier(table_name)
        quoted_column = self._quote_identifier(column_name)

        search_pattern = f"%{entity.strip().lower()}%"
        search_query = text(f"SELECT DISTINCT {quoted_column} FROM {quoted_table} WHERE {quoted_column} ILIKE :search_pattern")
        try:
            search_results = self.db.engine.connect().execute(
                search_query, {"search_pattern": search_pattern}
            ).fetchall()
            search_results = search_results[:25]
        except SQLAlchemyError:
            search_results = []
        distinct_query = text(f"SELECT DISTINCT {quoted_column} FROM {quoted_table}")
        results = self.db.engine.connect().execute(distinct_query).fetchall()
        results = self.find_similar_strings(results, entity)
        similar_items = "Similar items:\n"
        already_added = {}
        for item in results:
            similar_items += f"{item[0]}\n"
            already_added[item[0]] = True
        if len(search_results) > 0:
            for item in search_results:
                if item[0] not in already_added:
                    similar_items += f"{item[0]}\n"
        return similar_items
