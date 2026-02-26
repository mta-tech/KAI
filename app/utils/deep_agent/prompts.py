"""Prompt helpers for Deep Agent SQL generation."""

from __future__ import annotations

from textwrap import dedent
from typing import Iterable


DEFAULT_BEHAVIOR_INSTRUCTIONS = dedent(
    """
    You are KAI, a specialist who converts business questions into safe, read-only SQL.
    Always plan your work with write_todos, consult available schemas via the filesystem,
    and validate SQL using provided tools. Never perform DML/DDL operations or access
    data outside the tenant namespace provided to you.

    IMPORTANT: When you have completed the SQL generation, you MUST provide the final SQL
    in a markdown code block with the language identifier 'sql'. Format your final answer like this:

    ```sql
    SELECT * FROM table_name;
    ```

    This is the ONLY acceptable format for the final SQL output. Do not include any other text
    in the final answer besides the SQL code block.
    """
).strip()


def build_sql_agent_system_prompt(
    *,
    dialect: str,
    tenant_id: str,
    extra_instructions: Iterable[str] | None = None,
) -> str:
    """Return the base system prompt for Deep Agent SQL generation.

    Parameters
    ----------
    dialect:
        Target SQL dialect (postgresql/mysql/etc) used for contextual grounding.
    tenant_id:
        Current tenant identifier to reinforce isolation requirements.
    extra_instructions:
        Optional additional instruction snippets (strings) appended at the end.
    """

    instructions_block = "\n".join(extra_instructions or [])
    prompt = dedent(
        f"""
        {DEFAULT_BEHAVIOR_INSTRUCTIONS}

        Database dialect: {dialect}
        Tenant namespace: {tenant_id}

        Workflow:
          1. Break the request into todos (write_todos).
          2. Use filesystem tools to load schemas/aliases into your workspace.
          3. Draft SQL via the sql_drafter subagent.
          4. Validate using sql_validator before presenting a result.
          5. Stream intermediate progress to the user.
        {instructions_block}
        """
    ).strip()

    return prompt

