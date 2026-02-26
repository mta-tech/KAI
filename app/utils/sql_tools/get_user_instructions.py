from typing import List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from app.server.errors import sql_agent_exceptions


class GetUserInstructions(BaseTool):
    """Tool for retrieving the instructions from the user"""

    name: str = "GetAdminInstructions"
    description: str = """
    Input: is an empty string.
    Output: Database admin instructions before generating the SQL query.
    The generated SQL query MUST follow the admin instructions even if it contradicts with the given question.
    """
    instructions: List[dict]

    @sql_agent_exceptions()
    def _run(
        self,
        tool_input: str = "",  # noqa: ARG002
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        response = "Admin: All of the generated SQL queries must follow the below instructions:\n"
        for index, instruction in enumerate(self.instructions):
            response += f"{index + 1}) {instruction['instruction']}\n"
        return response
