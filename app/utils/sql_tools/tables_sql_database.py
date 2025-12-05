import logging
from typing import List

import numpy as np
import pandas as pd
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from langchain_core.embeddings import Embeddings
from pydantic import Field
from sql_metadata import Parser

from app.modules.table_description.models import TableDescription
from app.server.errors import sql_agent_exceptions

TOP_TABLES = 20

logger = logging.getLogger(__name__)


class TablesSQLDatabaseTool(BaseTool):
    """Tool which takes in the given question and returns a list of tables with their relevance score to the question"""

    name: str = "DbTablesWithRelevanceScores"
    description: str = """
    Input: Given question.
    Output: Comma-separated list of tables with their relevance scores, indicating their relevance to the question.
    Use this tool to identify the relevant tables for the given question.
    Only run this tool once and then go to the next plan even if the relevance score is low.
    """
    db_scan: List[TableDescription]
    embedding: Embeddings
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)

    def get_embedding(
        self,
        text: str,
    ) -> List[float]:
        text = text.replace("\n", " ")
        return self.embedding.embed_query(text)

    def get_docs_embedding(
        self,
        docs: List[str],
    ) -> List[List[float]]:
        return self.embedding.embed_documents(docs)

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b:  # Check for empty vectors
            return 0.0     
    
        if len(a) != len(b):  # Ensure both vectors have the same length
            raise ValueError("Vector embeddings must have the same length")

        if (np.linalg.norm(a) == 0) or (np.linalg.norm(b) == 0):  # Handle zero vectors
            return 0.0 
        
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    def similar_tables_based_on_few_shot_examples(self, df: pd.DataFrame) -> List[str]:
        most_similar_tables = set()
        if self.few_shot_examples is not None:
            for example in self.few_shot_examples:
                try:
                    tables = Parser(example["sql"]).tables
                except Exception as e:
                    logger.error(f"Error parsing SQL: {str(e)}")
                for table in tables:
                    found_tables = df[df.table_name == table]
                    for _, row in found_tables.iterrows():
                        most_similar_tables.add((row["db_schema"], row["table_name"]))
            df.drop(
                df[
                    df.table_name.isin([table[1] for table in most_similar_tables])
                ].index,
                inplace=True,
            )
        return most_similar_tables

    @sql_agent_exceptions()
    def _run(  # noqa: PLR0912
        self,
        user_question: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Use the concatenation of table name, columns names, and the description of the table as the table representation"""
        question_embedding = self.get_embedding(user_question)
        table_representations = []
        for table in self.db_scan:
            col_rep = ""
            for column in table.columns:
                if column.description is not None:
                    col_rep += f"{column.name}: {column.description}, "
                else:
                    col_rep += f"{column.name}, "
            if table.table_description is not None:
                table_rep = f"Table {table.table_name} contain columns: [{col_rep}], this tables has: {table.table_description}"
            else:
                table_rep = f"Table {table.table_name} contain columns: [{col_rep}]"
            table_representations.append([table.db_schema, table.table_name, table_rep])
        df = pd.DataFrame(
            table_representations,
            columns=["db_schema", "table_name", "table_representation"],
        )
        df["table_embedding"] = self.get_docs_embedding(df.table_representation)
        df["similarities"] = df.table_embedding.apply(
            lambda x: self.cosine_similarity(x, question_embedding)
        )
        df = df.sort_values(by="similarities", ascending=False)
        df = df.head(TOP_TABLES)
        max_similarities = max(df['similarities'])  # Store max similarity before modifying df
        most_similar_tables = self.similar_tables_based_on_few_shot_examples(df)
        table_relevance = ""
        for _, row in df.iterrows():
            if row["db_schema"] is not None:
                table_name = row["db_schema"] + "." + row["table_name"]
            else:
                table_name = row["table_name"]
            table_relevance += (
                f"Table: `{table_name}`, relevance score: {row['similarities']}\n"
            )
        if len(most_similar_tables) > 0:
            for table in most_similar_tables:
                if table[0] is not None:
                    table_name = table[0] + "." + table[1]
                else:
                    table_name = table[1]
                table_relevance += f"Table: `{table_name}`, relevance score: {max_similarities}\n"
        return table_relevance
