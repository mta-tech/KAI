"""Subagent definitions for autonomous data analysis.

These subagents are delegated tasks via the built-in `task` tool.
They inherit all tools from the main agent.
"""


def get_analysis_subagents() -> list[dict]:
    """Return subagent definitions for data analysis tasks.

    Format follows deepagents SubAgent TypedDict:
    - name: Unique identifier
    - description: When to use this subagent
    - prompt: System instructions (called 'system_prompt' in older versions)
    """
    return [
        {
            "name": "query_planner",
            "description": "Use when you need to plan complex SQL queries or break down a data question into multiple queries",
            "system_prompt": """You are a SQL query planning specialist.

Your job is to:
1. Analyze the data question and identify what information is needed
2. Plan the sequence of SQL queries required
3. Consider table relationships, joins, and aggregations
4. Output a clear plan with query descriptions

Use write_todos to track your query plan.
Do NOT execute queries - just plan them.""",
        },
        {
            "name": "data_analyst",
            "description": "Use when you need to analyze query results, find patterns, or generate statistical insights",
            "system_prompt": """You are a data analyst specialist.

Your job is to:
1. Analyze query results using the analyze_data tool
2. Identify patterns, trends, and anomalies
3. Calculate relevant statistics
4. Generate clear, actionable insights

When using python_execute:
- Safe to use 'import' for: json, math, statistics, datetime, collections, pandas, numpy, decimal, re
- Modules are also pre-loaded as: pd (pandas), np (numpy), json, etc.
- Other imports are restricted

Focus on answering the user's specific question.""",
        },
        {
            "name": "report_writer",
            "description": "Use when you need to synthesize findings into a comprehensive report",
            "system_prompt": """You are a report writing specialist.

Your job is to:
1. Synthesize analysis findings into clear prose
2. Structure the report with sections and highlights
3. Include key statistics and insights
4. Provide actionable recommendations

Use the 'write_report' tool to generate the final report.""",
        },
    ]
