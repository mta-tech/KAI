"""Alias lookup tool for Deep Agent usage."""

from __future__ import annotations

from typing import List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field

from app.server.errors import sql_agent_exceptions


class AliasLookupTool(BaseTool):
    """Tool that returns canonical table/column names for prompt aliases."""

    name: str = "AliasLookup"
    description: str = """
    Input: alias name mentioned in the question (case-insensitive).
    Output: canonical target name and target type.
    Use this tool when user questions include shorthand or business-specific aliases.
    """

    aliases: List[dict] = Field(default_factory=list)

    @sql_agent_exceptions()
    def _run(
        self,
        alias_name: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        alias_name = alias_name.strip().lower()
        if not alias_name:
            return "Provide an alias to look up."
        for alias in self.aliases:
            if alias.get("name", "").lower() == alias_name:
                target = alias.get("target_name", "unknown target")
                target_type = alias.get("target_type", "unknown type")
                return f"Alias '{alias_name}' refers to '{target}' ({target_type})."
        return f"Alias '{alias_name}' not found."

