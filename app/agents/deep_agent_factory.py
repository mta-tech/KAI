"""Factory for creating DeepAgent SQL agents."""

from __future__ import annotations


class DeepAgentRuntimeUnavailable(Exception):
    """Raised when deepagents runtime is unavailable."""


def create_kai_sql_agent(
    tenant_id,
    sql_generation_id,
    db_connection,
    database,
    tool_context,
    extra_instructions,
    llm_config,
):
    """Create a DeepAgent-based SQL generation agent.

    Args:
        tenant_id: Tenant identifier
        sql_generation_id: SQL generation session ID
        db_connection: Database connection object
        database: SQLDatabase instance
        tool_context: KaiToolContext object with schema info
        extra_instructions: Extra instructions for the agent
        llm_config: LLM configuration

    Returns:
        DeepAgent instance
    """
    # Lazy imports to avoid circular dependency
    from deepagents import create_deep_agent
    from deepagents.backends import CompositeBackend, StateBackend
    from app.utils.deep_agent.tools import build_tool_specs
    from app.utils.deep_agent.prompts import build_sql_agent_system_prompt
    from app.utils.model.chat_model import ChatModel

    # Get LLM instance
    chat_model = ChatModel()
    if llm_config:
        model_family = llm_config.model_family
        model_name = llm_config.model_name
    else:
        from app.server.config import get_settings  # type: ignore[attr-defined]
        settings = get_settings()
        model_family = settings.CHAT_FAMILY
        model_name = settings.CHAT_MODEL

    llm = chat_model.get_model(
        database_connection=db_connection,
        model_family=model_family,
        model_name=model_name,
        temperature=0.0
    )

    # Build system prompt
    dialect = database.dialect if hasattr(database, 'dialect') else 'postgresql'
    system_prompt = build_sql_agent_system_prompt(
        dialect=dialect,
        tenant_id=tenant_id or "default",
        extra_instructions=[extra_instructions] if extra_instructions else None
    )

    # Update tool context with IDs if not already set
    if hasattr(tool_context, 'tenant_id') and not tool_context.tenant_id:
        tool_context.tenant_id = tenant_id
    if hasattr(tool_context, 'sql_generation_id') and not tool_context.sql_generation_id:
        tool_context.sql_generation_id = sql_generation_id

    # Build tools - convert ToolSpec objects to actual tool instances
    tool_specs = build_tool_specs(tool_context)
    tools = [spec.build() for spec in tool_specs]

    # Create tool mapping by name for subagent configuration
    tools_by_name = {tool.name: tool for tool in tools}

    def get_tools(*names):
        """Get tools by name, filtering out missing ones."""
        return [tools_by_name[n] for n in names if n in tools_by_name]

    # Define subagents inline to avoid circular import
    subagents = [
        {
            "name": "schema_scout",
            "description": "Collects and summarizes relevant schemas before drafting SQL.",
            "system_prompt": (
                "You are responsible for identifying the smallest schema subset that"
                " satisfies the question. Output concise notes for the main agent."
            ),
            "tools": get_tools("table_schema", "tables_with_scores"),
        },
        {
            "name": "sql_drafter",
            "description": "Drafts candidate SQL based on the plan and schema notes.",
            "system_prompt": (
                "Focus on generating syntactically valid, read-only SQL. Use"
                " filesystem files for schema context and respect tenant isolation."
            ),
            "tools": get_tools("sql_db_query", "fewshot_examples"),
        },
        {
            "name": "sql_validator",
            "description": "Executes and validates SQL, fixing issues before final response.",
            "system_prompt": (
                "Run the SQL safely, capture errors, and iteratively refine. Do not"
                " return until the query succeeds or you have an actionable error."
            ),
            "tools": get_tools("sql_db_query"),
        },
    ]

    # Create backend factory
    def backend_factory(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),  # type: ignore[abstract]
            routes={},
        )

    # Create the deep agent
    agent = create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        subagents=subagents,  # type: ignore[arg-type]
        backend=backend_factory,
        checkpointer=None,
    )

    return agent
