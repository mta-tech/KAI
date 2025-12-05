"""LangGraph Evaluation Agent - replacement for deprecated ZeroShotAgent pattern."""

import logging
import re
import time
from difflib import SequenceMatcher
from typing import Annotated, Any, List

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.tool import (
    BaseSQLDatabaseTool,
    InfoSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from overrides import override
from pydantic import Field
from sqlalchemy import MetaData, Table, select

from app.modules.database_connection.models import DatabaseConnection
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import SQLGeneration
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_evaluator import Evaluation, Evaluator

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a {dialect} expert.
Given a question and a SQL query, analyze the correctness of the SQL query and provide a score as the final answer.
Score indicates how correctly and accurately SQL query answers the question.
Note that the score should be between 0 and 100. Higher scores means the SQL Query is more accurate.
Think step by step to provide the score.
Perform all of the below checks by using the tools:
1) columns used in the SELECT clause should correspond exactly to what user wants.
2) for each of the conditions in the WHERE clause:
    2.1) correct columns should be used to filter the rows (always use entity_finder tool to confirm the correctness)
    2.2) database value used in the condition should handle different scenarios or edge cases
3) all of the calculations should be double checked
4) nested queries and sub-queries should be broken down to simpler parts and all of those part should be checked.
5) the columns used for joining tables must have matching values in both tables
6) execute the given SQL query to check its results and compare it to the expectations
Always predict the score equal to zero if the query returns an empty result.

After your analysis, provide your final answer in this format:
Score: <number between 0 and 100>
"""


class EntityFinderTool(BaseSQLDatabaseTool, BaseTool):
    """Tool finding all syntactically similar entities from a database."""

    name: str = "entity_finder"
    description: str = """
    Input to this tool is an entity, a column, and the table containing the column.
    All the rows that have similar values to the given entity are returned.
    If the entity is not found, a not found message will be returned.
    Use this tool to check the correctness of conditions used in the WHERE clause.

    Input format: entity, column_name, table_name

    Example Input: David, name, singer
    """
    similarity_threshold: Annotated[float, Field(ge=0, le=1)] = 0.7
    number_similar_items: int = 20

    def similarity(self, first_string: str, second_string: str) -> float:
        return SequenceMatcher(None, first_string, second_string).ratio()

    def _run(
        self,
        input: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            response = ""
            entity, column_name, table_name = input.split(", ")
            engine = self.db._engine

            metadata = MetaData()
            metadata.reflect(bind=engine)
            table = Table(table_name, metadata, autoload=True)
            column = table.c[column_name]

            query = select(column.distinct()).select_from(table)

            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()

            similar_items = []
            for row in rows:
                pair_similarity = self.similarity(entity, str(row[0]))
                if pair_similarity > self.similarity_threshold:
                    similar_items.append({"row": str(row[0]), "score": pair_similarity})
            similar_items = sorted(
                similar_items, key=lambda x: x["score"], reverse=True
            )[: self.number_similar_items]
            for item in similar_items:
                response += f"Column {column_name}, contains -> {item['row']}.\n"

            if not response:
                response = f"Column {column_name} doesn't contain any value similar to {entity}"

            return response
        except Exception as e:
            return str(e)

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("EntityFinderTool does not support async")


def create_evaluation_tools(db: SQLDatabase) -> List[BaseTool]:
    """Create the tools for the evaluation agent."""
    info_sql_database_tool_description = (
        "Input to this tool is a comma-separated list of tables, output is the schema and sample first rows for those tables."
        "Use this tool to find the columns inside each table and their sample rows."
        "Example Input: table1, table2, table3"
    )
    info_sql_database_tool = InfoSQLDatabaseTool(
        db=db, description=info_sql_database_tool_description
    )

    query_sql_database_tool_description = (
        "Input to this tool is a SQL query, output is a result from the database. If the query is not correct, an error message "
        "will be returned. If an error is returned, rewrite the query and try again. If you encounter an issue with Unknown column "
        f"'xxxx' in 'field list', using {info_sql_database_tool.name} "
        "to query the correct table fields."
        "Use this tool to search for a specific value or to check a specific condition in the database."
    )
    query_sql_database_tool = QuerySQLDataBaseTool(
        db=db, description=query_sql_database_tool_description
    )

    entity_finder = EntityFinderTool(db=db)

    return [query_sql_database_tool, info_sql_database_tool, entity_finder]


class LangGraphEvaluationAgent(Evaluator):
    """LangGraph-based Evaluation Agent using create_react_agent."""

    sample_rows: int = 10
    llm: Any = None

    def answer_parser(self, answer: str) -> int:
        """
        Extract the number after the Score:
        If not found extract the last number between 0 and 100
        If not found return 0
        """
        pattern = r".*Score:\s*(\d+)"
        match = re.search(pattern, answer)
        output = 0
        if match:
            output = int(match.group(1))
        else:
            pattern = r"\b([0-9]{1,2}|100)\b"
            numbers = re.findall(pattern, answer)
            if numbers:
                output = int(numbers[-1])
        return output

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        """Evaluate SQL query using LangGraph ReAct agent."""
        start_time = time.time()
        logger.info(
            f"(LangGraph) Generating score for the question/sql pair: {str(user_prompt.text)}/ {str(sql_generation.sql)}"
        )

        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
            api_base=self.llm_config.api_base,
        )

        database = SQLDatabase.get_sql_engine(database_connection)
        database._sample_rows_in_table_info = self.sample_rows

        user_question = user_prompt.text
        sql = sql_generation.sql

        # Create tools
        tools = create_evaluation_tools(database)

        # Build system prompt with dialect
        system_prompt = SYSTEM_PROMPT.format(dialect=database.dialect)

        # Create the ReAct agent using langgraph.prebuilt
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=system_prompt,
        )

        # Create the user message
        user_message = f"""How accurately does the SQL query answer the question?
Give me a score between 0 and 100 by performing a step by step evaluation.

Question: {user_question}
SQL: {sql}
"""

        # Invoke the agent
        try:
            result = agent.invoke({
                "messages": [HumanMessage(content=user_message)]
            })

            # Extract the final answer
            messages = result.get("messages", [])
            answer = ""
            if messages:
                final_message = messages[-1]
                answer = final_message.content if hasattr(final_message, "content") else str(final_message)

            score = self.answer_parser(answer=answer) / 100

        except Exception as e:
            logger.exception(f"LangGraph evaluation agent failed: {str(e)}")
            score = 0

        end_time = time.time()
        logger.info(f"(LangGraph) Evaluation time elapsed: {str(end_time - start_time)}")

        return Evaluation(
            question_id=user_prompt.id, answer_id=sql_generation.id, score=score
        )
