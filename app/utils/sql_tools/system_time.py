from datetime import datetime

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool

from app.server.errors import sql_agent_exceptions


class SystemTime(BaseTool):
    """Tool for finding the current data and time."""

    name = "SystemTime"
    description = """
    Input is an empty string, output is the current data and time.
    Always use this tool before generating a query if there is any time or date in the given question.
    """

    @sql_agent_exceptions()
    def _run(
        self,
        tool_input: str = "",  # noqa: ARG002
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        current_datetime = datetime.now()
        return f"Current Date and Time: {str(current_datetime)}"
