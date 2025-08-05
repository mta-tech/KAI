from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from sqlalchemy import text

from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.nl_generation.models import NLGeneration
from app.modules.prompt.repositories import PromptRepository
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.utils.model.chat_model import ChatModel
from app.utils.nl_generator.nl_history import NLHistory
from app.utils.sql_database.sql_database import SQLDatabase

HUMAN_TEMPLATE = """Given a Question, a Sql query and the sql query result try to answer the question
If the sql query result doesn't answer the question just say 'I don't know'

{nl_history}

Answer the question given the sql query and the sql query result.
Question: {prompt}
SQL query: {sql_query}
SQL query result: {sql_query_result}
"""


class GeneratesNlAnswer:
    def __init__(self, storage, llm_config: LLMConfig):
        self.storage = storage
        self.llm_config = llm_config
        self.model = ChatModel()

    def execute(
        self,
        sql_generation: SQLGeneration,
        top_k: int = 100,
    ) -> NLGeneration:
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(sql_generation.prompt_id)

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            prompt.db_connection_id
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
            api_base=self.llm_config.api_base,
        )
        database = SQLDatabase.get_sql_engine(database_connection, False)

        if sql_generation.status == "INVALID":
            return NLGeneration(
                sql_generation_id=sql_generation.id,
                text="I don't know, the SQL query is invalid.",
                created_at=datetime.now(),
            )

        try:
            query = database.parser_to_filter_commands(sql_generation.sql)
            with database._engine.connect() as connection:
                execution = connection.execute(text(query))
                result = execution.mappings().fetchmany(top_k)

            rows = []
            for row in result:
                modified_row = {}
                for key, value in row.items():
                    if isinstance(
                        value, (date, datetime)
                    ):  # Check if the value is an instance of datetime.date
                        modified_row[key] = str(value)
                    elif isinstance(
                        value, Decimal
                    ):  # Check if the value is an instance of decimal.Decimal
                        modified_row[key] = float(value)
                    else:
                        modified_row[key] = value
                rows.append(modified_row)

        except Exception as e:
            raise HTTPException("Sensitive SQL keyword detected in the query.") from e

        nl_history = NLHistory.get_nl_history(prompt)
        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        nl_resp = chain.invoke(
            {
                "prompt": prompt.text,
                "sql_query": sql_generation.sql,
                "sql_query_result": "\n".join([str(row) for row in rows]),
                "nl_history": nl_history,
            }
        )

        nl_generation = NLGeneration(
            sql_generation_id=sql_generation.id,
            llm_config=self.llm_config,
            text=nl_resp["text"],
            created_at=str(datetime.now()),
        )
        return nl_generation
