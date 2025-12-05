"""Subagent presets for KAI deep agents.

This module defines subagent configurations in the native deepagents format (dicts).
"""

from __future__ import annotations

from typing import Dict, List

from app.agents.types import SubAgentSpec


def default_subagent_specs() -> List[SubAgentSpec]:
    """Return the default subagent definitions used by the SQL generator.
    
    Returns SubAgentSpec dataclasses for use with KaiAgentConfig.
    """
    return [
        SubAgentSpec(
            name="schema_scout",
            description="Collects and summarizes relevant schemas before drafting SQL.",
            tools=("table_schema", "tables_with_scores"),
            system_prompt=(
                "You are responsible for identifying the smallest schema subset that"
                " satisfies the question. Output concise notes for the main agent."
            ),
        ),
        SubAgentSpec(
            name="sql_drafter",
            description="Drafts candidate SQL based on the plan and schema notes.",
            tools=("sql_db_query", "fewshot_examples"),
            system_prompt=(
                "Focus on generating syntactically valid, read-only SQL. Use"
                " filesystem files for schema context and respect tenant isolation."
            ),
        ),
        SubAgentSpec(
            name="sql_validator",
            description="Executes and validates SQL, fixing issues before final response.",
            tools=("sql_db_query",),
            system_prompt=(
                "Run the SQL safely, capture errors, and iteratively refine. Do not"
                " return until the query succeeds or you have an actionable error."
            ),
            interrupt_on={"sql_db_query": True},
        ),
    ]


def default_subagent_dicts() -> List[Dict]:
    """Return the default subagent definitions in native deepagents format.
    
    This format is used directly by deepagents.create_deep_agent().
    Uses TypedDict keys: name, description, system_prompt, tools
    """
    return [
        {
            "name": "schema_scout",
            "description": "Collects and summarizes relevant schemas before drafting SQL.",
            "system_prompt": (
                "You are responsible for identifying the smallest schema subset that"
                " satisfies the question. Output concise notes for the main agent."
            ),
            "tools": ["table_schema", "tables_with_scores"],
        },
        {
            "name": "sql_drafter",
            "description": "Drafts candidate SQL based on the plan and schema notes.",
            "system_prompt": (
                "Focus on generating syntactically valid, read-only SQL. Use"
                " filesystem files for schema context and respect tenant isolation."
            ),
            "tools": ["sql_db_query", "fewshot_examples"],
        },
        {
            "name": "sql_validator",
            "description": "Executes and validates SQL, fixing issues before final response.",
            "system_prompt": (
                "Run the SQL safely, capture errors, and iteratively refine. Do not"
                " return until the query succeeds or you have an actionable error."
            ),
            "tools": ["sql_db_query"],
        },
    ]

