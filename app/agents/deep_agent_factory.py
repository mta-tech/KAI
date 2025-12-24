class DeepAgentRuntimeUnavailable(Exception):
    pass

def create_kai_sql_agent(
    tenant_id,
    sql_generation_id,
    db_connection,
    database,
    context,
    tool_context,
    metadata,
    extra_instructions,
    llm_config,
):
    """Stub for missing factory."""
    raise DeepAgentRuntimeUnavailable("Stub factory called")
