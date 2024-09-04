import difflib
from typing import List

from fastapi import HTTPException
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError

from app.modules.table_description.models import TableDescription
from app.server.errors import sql_agent_exceptions
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_tools import replace_unprocessable_characters


class ColumnEntityChecker(BaseTool):
    """Tool for checking the existance of an entity inside a column."""

    name = "DbColumnEntityChecker"
    description = """
    Input: Column name and its corresponding table, and an entity.
    Output: cell-values found in the column similar to the given entity.
    Use this tool to get cell values similar to the given entity in the given column.

    Example Input: table1 -> column2, entity
    """
    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List[TableDescription]
    is_multiple_schema: bool

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
                    "Table name should be in the format schema_name.table_name"
                )
        except ValueError:
            return "Invalid input format, use following format: table_name -> column_name, entity (entity should be a string without ',')"
        search_pattern = f"%{entity.strip().lower()}%"
        search_query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} ILIKE :search_pattern"  # noqa: S608
        try:
            search_results = self.db.engine.execute(
                search_query, {"search_pattern": search_pattern}
            ).fetchall()
            search_results = search_results[:25]
        except SQLAlchemyError:
            search_results = []
        distinct_query = f"SELECT DISTINCT {column_name} FROM {table_name}"  # noqa: S608
        results = self.db.engine.execute(distinct_query).fetchall()
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
