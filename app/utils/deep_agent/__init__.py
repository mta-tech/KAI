"""Utilities for wiring LangChain Deep Agents inside KAI."""

from importlib import import_module

__all__ = [
    "KaiToolContext",
    "build_sql_agent_system_prompt",
    "build_tool_specs",
    "default_subagent_specs",
    "build_middleware_stack",
]


def __getattr__(name):  # pragma: no cover - convenience bridge
    mapping = {
        "KaiToolContext": ("app.utils.deep_agent.tools", "KaiToolContext"),
        "build_tool_specs": ("app.utils.deep_agent.tools", "build_tool_specs"),
        "build_sql_agent_system_prompt": (
            "app.utils.deep_agent.prompts",
            "build_sql_agent_system_prompt",
        ),
        "default_subagent_specs": (
            "app.utils.deep_agent.subagents",
            "default_subagent_specs",
        ),
        "build_middleware_stack": (
            "app.utils.deep_agent.middleware",
            "build_middleware_stack",
        ),
    }
    if name not in mapping:
        raise AttributeError(name)
    module_name, attr = mapping[name]
    module = import_module(module_name)
    return getattr(module, attr)
