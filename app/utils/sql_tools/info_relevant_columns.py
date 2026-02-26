from typing import List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from app.modules.table_description.models import TableDescription
from app.server.errors import sql_agent_exceptions
from app.utils.sql_tools import replace_unprocessable_characters


class InfoRelevantColumns(BaseTool):
    """Tool for getting more information for potentially relevant columns"""

    name: str = "DbRelevantColumnsInfo"
    description: str = """
    Input: Comma-separated list of potentially relevant columns with their corresponding table.
    Output: Information about the values inside the columns and their descriptions.
    Use this tool to gather details about potentially relevant columns. then, filter them, and identify the relevant ones.

    Example Input: table1 -> column1, table1 -> column2, table2 -> column1
    """
    db_scan: List[TableDescription]

    @sql_agent_exceptions()
    def _run(  # noqa: C901, PLR0912
        self,
        column_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the column level information."""
        items_list = column_names.split(", ")
        column_full_info = ""
        for item in items_list:
            if " -> " in item:
                table_name, column_name = item.split(" -> ")
                if "." in table_name:
                    table_name = table_name.split(".")[1]
                table_name = replace_unprocessable_characters(table_name)
                column_name = replace_unprocessable_characters(column_name)
                found = False
                for table in self.db_scan:
                    if table_name == table.table_name:
                        col_info = ""
                        for column in table.columns:
                            if column_name == column.name:
                                found = True
                                col_info += f"Description: {column.description},"
                                if column.low_cardinality:
                                    col_info += f" categories = {column.categories},"
                        col_info += " Sample rows: "
                        if found:
                            for row in table.examples:
                                col_info += row[column_name] + ", "
                            col_info = col_info[:-2]
                            if table.db_schema:
                                schema_table = f"{table.db_schema}.{table.table_name}"
                            else:
                                schema_table = table.table_name
                            column_full_info += f"Table: {schema_table}, column: {column_name}, additional info: {col_info}\n"
            else:
                return "Malformed input, input should be in the following format Example Input: table1 -> column1, table1 -> column2, table2 -> column1"  # noqa: E501
            if not found:
                column_full_info += f"Table: {table_name}, column: {column_name} not found in database\n"
        return column_full_info
