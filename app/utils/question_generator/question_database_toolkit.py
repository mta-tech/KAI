from typing import List

from langchain_classic.agents.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool
from langchain_core.embeddings import Embeddings
from pydantic import Field

from app.modules.table_description.models import TableDescription
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_tools.column_entity_checker import ColumnEntityChecker
from app.utils.sql_tools.info_relevant_columns import InfoRelevantColumns
from app.utils.sql_tools.query_sql_database import QuerySQLDataBaseTool
from app.utils.sql_tools.schema_sql_database import SchemaSQLDatabaseTool
from app.utils.sql_tools.system_time import SystemTime
from app.utils.sql_tools.tables_sql_database import TablesSQLDatabaseTool


class QuestionDatabaseToolkit(BaseToolkit):
    """Available DB toolkit to generate context for question generation."""

    db: SQLDatabase = Field(exclude=True)
    db_scan: List[TableDescription] = Field(exclude=True)
    embedding: Embeddings = Field(exclude=True)
    is_multiple_schema: bool = False
    is_check_sql: bool = False

    @property
    def dialect(self) -> str:
        """Return string representation of SQL dialect to use."""
        return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        tools = []
        if self.is_check_sql:
            query_sql_db_tool = QuerySQLDataBaseTool(db=self.db)
            tools.append(query_sql_db_tool)
        get_current_datetime = SystemTime()
        tools.append(get_current_datetime)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db_scan=self.db_scan, embedding=self.embedding
        )
        tools.append(tables_sql_db_tool)
        schema_sql_db_tool = SchemaSQLDatabaseTool(db_scan=self.db_scan)
        tools.append(schema_sql_db_tool)
        info_relevant_tool = InfoRelevantColumns(db_scan=self.db_scan)
        tools.append(info_relevant_tool)
        column_sample_tool = ColumnEntityChecker(
            db=self.db,
            db_scan=self.db_scan,
            is_multiple_schema=self.is_multiple_schema,
        )
        tools.append(column_sample_tool)
        return tools
