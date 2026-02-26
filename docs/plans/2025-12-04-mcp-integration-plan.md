# MCP (Model Context Protocol) Integration Plan

## Overview

Add MCP support to KAI autonomous agent, enabling dynamic tool discovery and integration from external MCP servers. This allows KAI to leverage the growing ecosystem of MCP tools (databases, APIs, file systems, etc.) alongside its existing native tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KAI Autonomous Agent                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │  Native Tools   │    │   MCP Adapter   │    │  DeepAgents     │     │
│  │  - sql_query    │    │                 │    │  Built-in Tools │     │
│  │  - schema       │    │  MultiServer    │    │  - write_todos  │     │
│  │  - memory       │    │  MCPClient      │    │  - read_file    │     │
│  │  - skills       │    │                 │    │  - task         │     │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘     │
│           │                      │                      │               │
│           └──────────────────────┼──────────────────────┘               │
│                                  │                                      │
│                        ┌─────────▼─────────┐                            │
│                        │   Tool Registry   │                            │
│                        │   (Combined)      │                            │
│                        └─────────┬─────────┘                            │
│                                  │                                      │
│                        ┌─────────▼─────────┐                            │
│                        │  create_deep_agent │                            │
│                        └───────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
              │ MCP Server│  │ MCP Server│  │ MCP Server│
              │ (stdio)   │  │ (HTTP)    │  │ (SSE)     │
              │ e.g. FS   │  │ e.g. API  │  │ e.g. DB   │
              └───────────┘  └───────────┘  └───────────┘
```

## Implementation Phases

### Phase 1: Core MCP Integration

**Files to create/modify:**

1. **`app/modules/mcp/__init__.py`** (new)
   - MCP module initialization

2. **`app/modules/mcp/client.py`** (new)
   - `MCPToolManager` class - manages MCP server connections
   - Wraps `MultiServerMCPClient` from langchain-mcp-adapters
   - Provides tool loading with error handling
   - Caches loaded tools per session

3. **`app/modules/mcp/config.py`** (new)
   - MCP server configuration model
   - Support for stdio, streamable_http, sse transports

4. **`app/server/config.py`** (modify)
   - Add MCP configuration settings
   - `MCP_SERVERS_CONFIG_FILE`: Path to MCP servers config JSON
   - `MCP_ENABLED`: Toggle MCP integration

5. **`pyproject.toml`** (modify)
   - Add `langchain-mcp-adapters>=0.1.14` dependency

### Phase 2: Agent Integration

**Files to modify:**

1. **`app/modules/autonomous_agent/service.py`**
   - Modify `_build_tools()` to include MCP tools
   - Add `_load_mcp_tools()` method
   - Handle async tool loading in sync context

2. **`app/modules/autonomous_agent/cli.py`**
   - Add `--mcp-config` option for custom config file
   - Add `/mcp` command to list available MCP tools
   - Add `/mcp-reload` to refresh MCP connections

### Phase 3: Configuration & Management

**Files to create:**

1. **`mcp-servers.json`** (example config)
   ```json
   {
     "servers": {
       "filesystem": {
         "transport": "stdio",
         "command": "npx",
         "args": ["-y", "@anthropic/mcp-filesystem", "/path/to/allowed/dir"]
       },
       "github": {
         "transport": "stdio",
         "command": "npx",
         "args": ["-y", "@anthropic/mcp-github"],
         "env": {
           "GITHUB_TOKEN": "${GITHUB_TOKEN}"
         }
       },
       "custom-api": {
         "transport": "streamable_http",
         "url": "http://localhost:8080/mcp",
         "headers": {
           "Authorization": "Bearer ${API_TOKEN}"
         }
       }
     }
   }
   ```

2. **`.env.example`** (modify)
   - Add MCP-related environment variables

---

## Detailed Implementation

### 1. MCP Client Module (`app/modules/mcp/client.py`)

```python
"""MCP Tool Manager for KAI autonomous agent."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class MCPToolManager:
    """Manages MCP server connections and tool loading.

    Provides a high-level interface for loading tools from multiple
    MCP servers and integrating them with the KAI agent.
    """

    def __init__(self, config_path: str | Path | None = None):
        """Initialize MCP tool manager.

        Args:
            config_path: Path to MCP servers configuration JSON file.
        """
        self.config_path = Path(config_path) if config_path else None
        self._client = None
        self._tools_cache: list[BaseTool] = []
        self._initialized = False

    def _load_config(self) -> dict[str, Any]:
        """Load MCP servers configuration from file."""
        if not self.config_path or not self.config_path.exists():
            return {"servers": {}}

        with open(self.config_path) as f:
            config = json.load(f)

        # Expand environment variables in config
        return self._expand_env_vars(config)

    def _expand_env_vars(self, config: dict) -> dict:
        """Recursively expand ${VAR} placeholders in config."""
        if isinstance(config, dict):
            return {k: self._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            return os.environ.get(var_name, "")
        return config

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
            return

        config = self._load_config()
        servers = config.get("servers", {})

        if not servers:
            logger.info("No MCP servers configured")
            return

        try:
            self._client = MultiServerMCPClient(servers)
            self._tools_cache = await self._client.get_tools()
            self._initialized = True
            logger.info(
                f"Loaded {len(self._tools_cache)} tools from "
                f"{len(servers)} MCP server(s)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self._tools_cache = []

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
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(self.initialize())
            finally:
                loop.close()
        return self._tools_cache

    async def reload(self) -> None:
        """Reload MCP tools from all servers."""
        self._initialized = False
        self._tools_cache = []
        await self.initialize()

    def list_servers(self) -> list[str]:
        """List configured MCP server names."""
        config = self._load_config()
        return list(config.get("servers", {}).keys())
```

### 2. Service Integration (`app/modules/autonomous_agent/service.py`)

Add MCP tool loading to `_build_tools()`:

```python
def _build_tools(self, results_dir: str) -> list:
    """Build KAI-specific tools including MCP tools."""
    tools = [
        # Existing native tools...
        create_schema_context_tool(self.db_connection, self.storage),
        create_sql_query_tool(self.database),
        # ... etc
    ]

    # Load MCP tools if enabled
    mcp_tools = self._load_mcp_tools()
    if mcp_tools:
        tools.extend(mcp_tools)
        logger.info(f"Added {len(mcp_tools)} MCP tools to agent")

    return tools

def _load_mcp_tools(self) -> list:
    """Load tools from configured MCP servers."""
    from app.server.config import Settings
    settings = Settings()

    if not getattr(settings, "MCP_ENABLED", False):
        return []

    config_path = getattr(settings, "MCP_SERVERS_CONFIG", None)
    if not config_path:
        return []

    try:
        from app.modules.mcp.client import MCPToolManager
        manager = MCPToolManager(config_path)
        return manager.get_tools_sync()
    except Exception as e:
        logger.warning(f"Failed to load MCP tools: {e}")
        return []
```

### 3. Configuration (`app/server/config.py`)

```python
# MCP (Model Context Protocol) integration
MCP_ENABLED: bool = False
MCP_SERVERS_CONFIG: str | None = None  # Path to mcp-servers.json
```

### 4. CLI Commands (`app/modules/autonomous_agent/cli.py`)

Add MCP-related commands:

```python
@cli.command()
@click.option("--config", "config_path", help="Path to MCP servers config")
def mcp_list(config_path: str | None):
    """List available MCP tools."""
    from app.modules.mcp.client import MCPToolManager
    from app.server.config import Settings

    settings = Settings()
    path = config_path or settings.MCP_SERVERS_CONFIG

    if not path:
        console.print("[yellow]No MCP config specified[/yellow]")
        return

    manager = MCPToolManager(path)
    tools = manager.get_tools_sync()

    console.print(f"\n[bold]MCP Tools ({len(tools)} available):[/bold]\n")
    for tool in tools:
        console.print(f"  • [cyan]{tool.name}[/cyan]: {tool.description[:60]}...")
```

---

## Dependencies

Add to `pyproject.toml`:

```toml
dependencies = [
    # ... existing deps
    "langchain-mcp-adapters>=0.1.14",
]
```

---

## Configuration Example

**`mcp-servers.json`:**

```json
{
  "servers": {
    "filesystem": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
      "description": "File system access for data files"
    },
    "postgres-tools": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_URL": "${DATABASE_URL}"
      }
    },
    "custom-api": {
      "transport": "streamable_http",
      "url": "http://internal-api:8080/mcp",
      "headers": {
        "X-API-Key": "${INTERNAL_API_KEY}"
      }
    }
  }
}
```

**`.env`:**

```bash
# MCP Configuration
MCP_ENABLED=true
MCP_SERVERS_CONFIG=./mcp-servers.json
```

---

## Usage Examples

### Interactive Session with MCP Tools

```bash
# Start with MCP enabled
kai-agent interactive --db conn_123

# In session, MCP tools are automatically available
kai> Use the filesystem tool to read /data/report.csv and analyze it
```

### List Available MCP Tools

```bash
kai-agent mcp-list --config ./mcp-servers.json
```

---

## Testing Strategy

1. **Unit Tests:**
   - `test_mcp_config_loading` - Validate config parsing
   - `test_env_var_expansion` - Test ${VAR} substitution
   - `test_mcp_tool_loading` - Mock MCP client, verify tool list

2. **Integration Tests:**
   - `test_mcp_with_agent` - Full agent with MCP tools
   - `test_mcp_server_failure` - Graceful handling of server errors

3. **Manual Testing:**
   - Test with official MCP servers (filesystem, GitHub)
   - Test with custom HTTP server

---

## Error Handling

1. **Server Connection Failures:**
   - Log warning, continue without MCP tools
   - Don't block agent startup

2. **Tool Execution Failures:**
   - Return structured error response
   - Allow agent to retry or use alternative approach

3. **Configuration Errors:**
   - Validate config on load
   - Clear error messages for missing env vars

---

## Future Enhancements

1. **Per-Connection MCP Config:**
   - Allow different MCP servers per database connection
   - Store config in database_connection metadata

2. **MCP Resources:**
   - Expose MCP resources as context
   - Auto-load relevant resources for queries

3. **MCP Prompts:**
   - Use MCP prompts as skill templates
   - Integrate with existing skills system

4. **Dynamic Server Discovery:**
   - Support MCP server registry
   - Auto-discover available tools

---

## Timeline Estimate

- **Phase 1 (Core):** Create MCP module, client wrapper, config
- **Phase 2 (Integration):** Integrate with agent service
- **Phase 3 (CLI/Config):** Add CLI commands, documentation

---

## References

- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
