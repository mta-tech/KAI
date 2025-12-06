"""MCP Tool Manager for KAI autonomous agent."""

import asyncio
import io
import json
import logging
import os
import sys
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Keys not supported by LangChain tool schemas
UNSUPPORTED_SCHEMA_KEYS = {"$schema", "additionalProperties"}

# Default timeout for HTTP server connections (seconds)
DEFAULT_HTTP_TIMEOUT = 5.0

# Dangerous tool patterns that require explicit whitelisting
DANGEROUS_TOOL_PATTERNS = [
    "shell", "exec", "run_command", "execute_command",
    "system", "subprocess", "bash", "cmd", "powershell",
    "delete", "drop", "truncate", "rm", "rmdir",
    "write_file", "create_file", "modify_file",
]

# Tools that are always blocked (security critical)
BLOCKED_TOOLS = {
    "shell_exec",
    "run_arbitrary_command",
    "eval",
    "exec_code",
}


@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output (hide library tracebacks)."""
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stderr = old_stderr


async def _check_http_server(url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> bool:
    """Check if an HTTP server is reachable.

    Args:
        url: The server URL to check.
        timeout: Connection timeout in seconds.

    Returns:
        True if server is reachable, False otherwise.
    """
    try:
        import httpx

        async with httpx.AsyncClient(timeout=timeout) as client:
            # Just try to connect, don't care about the response
            response = await client.head(url)
            return True
    except Exception:
        return False


def _check_http_server_sync(url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> bool:
    """Check if an HTTP server is reachable (sync version).

    Args:
        url: The server URL to check.
        timeout: Connection timeout in seconds.

    Returns:
        True if server is reachable, False otherwise.
    """
    try:
        import httpx

        with httpx.Client(timeout=timeout) as client:
            response = client.head(url)
            return True
    except Exception:
        return False


def _sanitize_tool_schema(tool: BaseTool) -> BaseTool:
    """Remove unsupported keys from tool's args_schema to prevent warnings.

    Args:
        tool: LangChain tool with potential unsupported schema keys.

    Returns:
        The same tool with sanitized schema.
    """
    if hasattr(tool, "args_schema") and tool.args_schema is not None:
        schema = tool.args_schema
        # Handle Pydantic model schema
        if hasattr(schema, "model_json_schema"):
            # Can't modify Pydantic schema directly, warnings are harmless
            pass
        elif hasattr(schema, "schema") and callable(schema.schema):
            # Pydantic v1 style
            pass
    return tool


def _is_dangerous_tool(tool_name: str) -> bool:
    """Check if a tool name matches dangerous patterns.

    Args:
        tool_name: The tool name to check.

    Returns:
        True if the tool matches dangerous patterns.
    """
    tool_lower = tool_name.lower()

    # Check blocked list first
    if tool_lower in BLOCKED_TOOLS:
        return True

    # Check dangerous patterns
    return any(pattern in tool_lower for pattern in DANGEROUS_TOOL_PATTERNS)


class MCPToolManager:
    """Manages MCP server connections and tool loading.

    Provides a high-level interface for loading tools from multiple
    MCP servers and integrating them with the KAI agent.

    Security features:
    - Tool whitelisting support
    - Dangerous tool pattern detection
    - Blocked tool list
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        allowed_tools: set[str] | None = None,
        block_dangerous: bool = True,
    ):
        """Initialize MCP tool manager.

        Args:
            config_path: Path to MCP servers configuration JSON file.
            allowed_tools: Optional whitelist of allowed tool names.
                          If None, all non-dangerous tools are allowed.
            block_dangerous: If True, block tools matching dangerous patterns.
        """
        self.config_path = Path(config_path) if config_path else None
        self.allowed_tools = allowed_tools
        self.block_dangerous = block_dangerous
        self._client = None
        self._tools_cache: list[BaseTool] = []
        self._initialized = False
        self._loop = None
        self._blocked_tools: list[str] = []  # Track blocked tools for logging

    def _load_config(self) -> dict[str, Any]:
        """Load MCP servers configuration from file."""
        if not self.config_path or not self.config_path.exists():
            return {"servers": {}}

        with open(self.config_path) as f:
            config = json.load(f)

        # Expand environment variables in config
        return self._expand_env_vars(config)

    def _expand_env_vars(self, config: Any) -> Any:
        """Recursively expand ${VAR} placeholders in config."""
        if isinstance(config, dict):
            return {k: self._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            return os.environ.get(var_name, "")
        return config

    async def _filter_reachable_servers(self, servers: dict[str, Any]) -> dict[str, Any]:
        """Filter out HTTP servers that are unreachable.

        Args:
            servers: Server configuration dictionary.

        Returns:
            Filtered servers with only reachable HTTP servers and all stdio servers.
        """
        reachable = {}

        for name, config in servers.items():
            transport = config.get("transport", "stdio")

            if transport in ("streamable_http", "sse"):
                # HTTP-based server - check if reachable
                url = config.get("url", "")
                if url:
                    is_reachable = await _check_http_server(url)
                    if is_reachable:
                        reachable[name] = config
                    else:
                        logger.info(f"MCP server '{name}' at {url} is not reachable, skipping")
                else:
                    logger.warning(f"MCP server '{name}' has no URL configured, skipping")
            else:
                # stdio server - always include (will fail gracefully if command not found)
                reachable[name] = config

        return reachable

    async def initialize(self) -> None:
        """Initialize MCP client and load tools from all servers."""
        if self._initialized:
            return

        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
        except ImportError:
            logger.warning(
                "langchain-mcp-adapters not installed. "
                "Install with: pip install langchain-mcp-adapters"
            )
            self._initialized = True
            return

        config = self._load_config()
        servers = config.get("servers", {})

        if not servers:
            logger.info("No MCP servers configured")
            self._initialized = True
            return

        # Filter out unreachable HTTP servers to prevent timeout errors
        reachable_servers = await self._filter_reachable_servers(servers)

        if not reachable_servers:
            logger.info("No reachable MCP servers found")
            self._tools_cache = []
            self._initialized = True
            return

        try:
            # Suppress stderr to hide library tracebacks during initialization
            with suppress_stderr():
                # Create client and get tools directly (no context manager in v0.1.0+)
                self._client = MultiServerMCPClient(reachable_servers)
                tools = await self._client.get_tools()

            # Filter and sanitize tools based on security settings
            filtered_tools = []
            self._blocked_tools = []

            for tool in tools:
                tool_name = tool.name

                # Check if tool is in whitelist (if whitelist is configured)
                if self.allowed_tools is not None:
                    if tool_name not in self.allowed_tools:
                        self._blocked_tools.append(f"{tool_name} (not in whitelist)")
                        continue

                # Check if tool matches dangerous patterns
                if self.block_dangerous and _is_dangerous_tool(tool_name):
                    self._blocked_tools.append(f"{tool_name} (dangerous pattern)")
                    logger.warning(f"Blocked dangerous MCP tool: {tool_name}")
                    continue

                filtered_tools.append(_sanitize_tool_schema(tool))

            self._tools_cache = filtered_tools
            self._initialized = True

            if self._blocked_tools:
                logger.info(
                    f"Loaded {len(self._tools_cache)} tools from "
                    f"{len(reachable_servers)} MCP server(s), "
                    f"blocked {len(self._blocked_tools)} dangerous tools"
                )
            else:
                logger.info(
                    f"Loaded {len(self._tools_cache)} tools from "
                    f"{len(reachable_servers)} MCP server(s)"
                )
        except Exception as e:
            # Log warning but don't fail - agent can work without MCP tools
            logger.warning(f"MCP initialization failed (agent will continue without MCP tools): {e}")
            self._tools_cache = []
            self._initialized = True  # Mark as initialized to prevent retries

    def get_tools(self) -> list[BaseTool]:
        """Get cached MCP tools.

        Returns:
            List of LangChain-compatible tools from MCP servers.
        """
        return self._tools_cache

    def get_tools_sync(self) -> list[BaseTool]:
        """Synchronously get MCP tools (initializes if needed).

        Returns:
            List of LangChain-compatible tools from MCP servers.
        """
        if not self._initialized:
            # Suppress schema warnings during initialization
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*is not supported in schema.*",
                )
                try:
                    # Check if we're in an async context
                    asyncio.get_running_loop()
                    # We're in async context - use nest_asyncio or thread pool
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(self._run_init_in_new_loop)
                        future.result()
                except RuntimeError:
                    # No running loop, create one and keep it for cleanup
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
                    try:
                        self._loop.run_until_complete(self.initialize())
                    except Exception as e:
                        logger.error(f"Failed to initialize MCP: {e}")
                        self._cleanup_loop()
        return self._tools_cache

    def _run_init_in_new_loop(self) -> None:
        """Run initialization in a new event loop (for thread pool)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.initialize())
        finally:
            # Clean up pending tasks before closing
            self._cancel_pending_tasks(loop)
            loop.close()

    def _cancel_pending_tasks(self, loop: asyncio.AbstractEventLoop) -> None:
        """Cancel all pending tasks in the event loop."""
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
        except Exception:
            pass

    def _cleanup_loop(self) -> None:
        """Clean up the event loop properly."""
        if self._loop and not self._loop.is_closed():
            try:
                self._cancel_pending_tasks(self._loop)
                self._loop.close()
            except Exception:
                pass
            self._loop = None

    async def reload(self) -> None:
        """Reload MCP tools from all servers."""
        self._initialized = False
        self._tools_cache = []
        self._client = None
        await self.initialize()

    def list_servers(self) -> list[str]:
        """List configured MCP server names."""
        config = self._load_config()
        return list(config.get("servers", {}).keys())

    def get_server_info(self) -> dict[str, Any]:
        """Get detailed information about configured servers."""
        config = self._load_config()
        servers = config.get("servers", {})

        info = {}
        for name, server_config in servers.items():
            info[name] = {
                "transport": server_config.get("transport", "unknown"),
                "command": server_config.get("command"),
                "url": server_config.get("url"),
            }
        return info

    def get_blocked_tools(self) -> list[str]:
        """Get list of tools that were blocked for security reasons.

        Returns:
            List of blocked tool names with reasons.
        """
        return self._blocked_tools.copy()

    def get_security_info(self) -> dict[str, Any]:
        """Get security configuration info.

        Returns:
            Dictionary with security settings and blocked tools.
        """
        return {
            "block_dangerous": self.block_dangerous,
            "whitelist_enabled": self.allowed_tools is not None,
            "whitelist_size": len(self.allowed_tools) if self.allowed_tools else 0,
            "blocked_tools_count": len(self._blocked_tools),
            "blocked_tools": self._blocked_tools,
            "dangerous_patterns": DANGEROUS_TOOL_PATTERNS,
            "always_blocked": list(BLOCKED_TOOLS),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._client = None
        self._initialized = False
        self._tools_cache = []
