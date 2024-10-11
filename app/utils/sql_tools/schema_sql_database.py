from typing import List

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool

from app.modules.table_description.models import TableDescription
from app.server.errors import sql_agent_exceptions
from app.utils.sql_tools import replace_unprocessable_characters


class SchemaSQLDatabaseTool(BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "DbRelevantTablesSchema"
    description = """
    Input: Comma-separated list of tables.
    Output: Schema of the specified tables.
    Use this tool to discover all columns of the relevant tables and identify potentially relevant columns.

    Example Input: table1, table2, table3
    """
    db_scan: List[TableDescription]

    @sql_agent_exceptions()
    def _run(  # noqa: C901
        self,
        table_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        table_names_list = table_names.split(", ")
        processed_table_names = []
        for table in table_names_list:
            formatted_table = replace_unprocessable_characters(table)
            if "." in formatted_table:
                processed_table_names.append(formatted_table.split(".")[1])
            else:
                processed_table_names.append(formatted_table)
        tables_schema = "```sql\n"
        for table in self.db_scan:
            if table.table_name in processed_table_names:
                tables_schema += table.table_schema + "\n"
                descriptions = []
                if table.table_description is not None:
                    if table.db_schema:
                        table_name = f"{table.db_schema}.{table.table_name}"
                    else:
                        table_name = table.table_name
                    descriptions.append(
                        f"Table `{table_name}`: {table.table_description}\n"
                    )
                    for column in table.columns:
                        if column.description is not None:
                            descriptions.append(
                                f"Column `{column.name}`: {column.description}\n"
                            )
                if len(descriptions) > 0:
                    tables_schema += f"/*\n{''.join(descriptions)}*/\n"
        tables_schema += "```\n"
        if tables_schema == "":
            tables_schema += "Tables not found in the database"
        return tables_schema
