from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools.base import BaseTool
from langchain_core.embeddings import Embeddings
from pydantic import Field

from app.modules.table_description.models import TableDescription
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_tools.column_entity_checker import ColumnEntityChecker

# from app.utils.sql_tools.get_few_shot_examples import GetFewShotExamples
# from app.utils.sql_tools.get_user_instructions import GetUserInstructions
from app.utils.sql_tools.info_relevant_columns import InfoRelevantColumns
from app.utils.sql_tools.query_sql_database import QuerySQLDataBaseTool
from app.utils.sql_tools.schema_sql_database import SchemaSQLDatabaseTool
from app.utils.sql_tools.system_time import SystemTime
from app.utils.sql_tools.tables_sql_database import TablesSQLDatabaseTool


class SQLDatabaseToolkitDev(BaseToolkit):
    """Available toolkit"""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)
    business_metrics: List[dict] | None = Field(exclude=True, default=None)
    instructions: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List[TableDescription] = Field(exclude=True)
    embedding: Embeddings = Field(exclude=True)
    is_multiple_schema: bool = False

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
        query_sql_db_tool = QuerySQLDataBaseTool(db=self.db, context=self.context)
        tools.append(query_sql_db_tool)
        get_current_datetime = SystemTime()
        tools.append(get_current_datetime)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db_scan=self.db_scan,
            embedding=self.embedding,
            few_shot_examples=self.few_shot_examples,
        )
        tools.append(tables_sql_db_tool)
        schema_sql_db_tool = SchemaSQLDatabaseTool(db_scan=self.db_scan)
        tools.append(schema_sql_db_tool)
        info_relevant_tool = InfoRelevantColumns(db_scan=self.db_scan)
        tools.append(info_relevant_tool)
        column_sample_tool = ColumnEntityChecker(
            db=self.db,
            context=self.context,
            db_scan=self.db_scan,
            is_multiple_schema=self.is_multiple_schema,
        )
        tools.append(column_sample_tool)
        return tools
