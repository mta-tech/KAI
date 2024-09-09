from typing import List

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool

from app.server.errors import sql_agent_exceptions


class GetFewShotExamples(BaseTool):
    """Tool to obtain few-shot examples from the pool of samples"""

    name = "FewshotExamplesRetriever"
    description = """
    Input: Number of required Question/SQL pairs.
    Output: List of similar Question/SQL pairs related to the given question.
    Use this tool to fetch previously asked Question/SQL pairs as examples for improving SQL query generation.
    For complex questions, request more examples to gain a better understanding of tables and columns and the SQL keywords to use.
    If the given question is very similar to one of the retrieved examples, it is recommended to use the same SQL query and modify it slightly to fit the given question.
    Always use this tool first and before any other tool!
    """  # noqa: E501
    few_shot_examples: List[dict]
    

    @sql_agent_exceptions()
    def _run(
        self,
        number_of_samples: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        if number_of_samples.strip().isdigit():
            number_of_samples = int(number_of_samples.strip())
        else:
            return "Action input for the fewshot_examples_retriever tool should be an integer"
        returned_output = ""
        for example in self.few_shot_examples[:number_of_samples]:
            returned_output += f"Question: {example['prompt']} \n"
            returned_output += f"```sql\n{example['sql']}\n```\n"
        if returned_output == "":
            returned_output = "No previously asked Question/SQL pairs are available"
        return returned_output
