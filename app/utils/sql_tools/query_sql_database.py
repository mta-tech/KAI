import os
from typing import List
import re

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from pydantic import Field

from app.server.errors import sql_agent_exceptions
from app.utils.core.timeout import run_with_timeout
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_tools import replace_unprocessable_characters

TOP_K = SQLGenerator.get_upper_bound_limit()


class QuerySQLDataBaseTool(BaseTool):
    """Tool for querying a SQL database."""

    name: str = "SqlDbQuery"
    description: str = """
    Input: -- A well-formed multi-line SQL query between ```sql and ``` tags.
    Output: Result from the database or an error message if the query is incorrect.
    If an error occurs, rewrite the query and retry.
    Use this tool to execute SQL queries.
    Add newline after both ```sql and ``` tags.
    """

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)

    @sql_agent_exceptions()
    def _run(
        self,
        query: str,
        top_k: int = TOP_K,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        query = replace_unprocessable_characters(query)
        if "```sql" in query:
            query = re.sub(r"`{3,}sql", "", query)  # Remove triple or more backticks followed by 'sql'
            query = re.sub(r"`{3,}", "", query)      # Remove triple or more backticks

        try:
            return run_with_timeout(
                self.db.run_sql,
                args=(query,),
                kwargs={"top_k": top_k},
                timeout_duration=int(os.getenv("SQL_EXECUTION_TIMEOUT", "60")),
            )[0]
        except TimeoutError:
            return "SQL query execution time exceeded, proceed without query execution"
