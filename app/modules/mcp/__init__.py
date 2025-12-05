"""MCP (Model Context Protocol) integration module for KAI autonomous agent.

This module provides dynamic tool discovery and integration from external
MCP servers, allowing KAI to leverage the growing ecosystem of MCP tools
(databases, APIs, file systems, etc.) alongside its existing native tools.
"""

from contextlib import contextmanager

from app.modules.mcp.client import MCPToolManager

__all__ = ["MCPToolManager", "suppress_schema_warnings", "install_schema_warning_filter"]

# Suppress noisy LangChain schema warnings for MCP tools
_filter_installed = False


def install_schema_warning_filter():
    """Install a filter to suppress LangChain schema warnings.

    Patches langchain_google_genai._function_utils to not log warnings about
    unsupported schema keys ($schema, additionalProperties, etc.).
    """
    global _filter_installed
    if _filter_installed:
        return

    try:
        # The warnings come from langchain_google_genai, not langchain_core
        import logging

        # Get the logger used by langchain_google_genai
        google_logger = logging.getLogger("langchain_google_genai._function_utils")

        # Add a filter to suppress schema warnings
        class SchemaWarningFilter(logging.Filter):
            def filter(self, record):
                msg = record.getMessage()
                if "is not supported in schema" in msg:
                    return False  # Suppress this message
                return True  # Allow other messages

        google_logger.addFilter(SchemaWarningFilter())
        _filter_installed = True

    except Exception:
        # If patching fails, continue without filtering
        pass


@contextmanager
def suppress_schema_warnings():
    """Context manager to temporarily suppress schema warnings."""
    # Just install the filter if not already done
    install_schema_warning_filter()
    yield
