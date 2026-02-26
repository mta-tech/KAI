---
title: refactor: CLI Command Groups
type: refactor
date: 2026-01-29
---

# Refactor KAI CLI to Command Groups

## Overview

Refactor the KAI CLI from a flat 59-command structure (4,631 lines in a single file) to organized domain-based groups, improving discoverability, reducing code complexity, and enhancing user experience.

**Current State:**
- 59 commands in a flat structure under `app/modules/autonomous_agent/cli.py`
- 4,631 lines in a single file
- MDL group already implemented as proof-of-concept (lines 4197+)

**Target State:**
- 8 domain-based command groups
- Modular CLI files split by domain (~200-600 lines each)
- Main `cli.py` reduced to ~200 lines as a simple router
- Breaking changes (no backward compatibility)

## Problem Statement / Motivation

### Why This Refactor?

1. **Discoverability**: With 59 commands in a flat structure, users struggle to find relevant commands
2. **Maintainability**: A 4,631-line file is difficult to navigate, modify, and test
3. **User Experience**: Modern CLIs (git, docker, kubectl) use grouped commands for better organization
4. **Development Velocity**: Modular structure enables parallel development by domain

### Success Criteria

- [ ] Main `cli.py` reduced from 4,631 to ~200 lines
- [ ] All 59 commands successfully migrated to new group structure
- [ ] Query workflow (connection → table → query → session) works end-to-end
- [ ] Each CLI module independently testable
- [ ] Documentation updated with new command examples
- [ ] Tests added for all command groups

## Proposed Solution

### Command Group Structure

**8 domain-based groups:**

```bash
kai connection <command>      # Database connection management (6 commands)
kai table <command>           # Table/schema management (5 commands)
kai query <command>           # Query execution and analysis (4 commands)
kai session <command>         # Conversation session management (6 commands)
kai dashboard <command>       # Dashboard management (7 commands)
kai knowledge <command>       # Glossary, instructions, skills, memory (24 commands)
kai mdl <command>             # MDL semantic layer (2 commands, already exists)
kai config <command>          # Configuration and system utilities (4 commands)
```

### File Organization

**New structure:**

```
app/modules/autonomous_agent/
├── cli.py                    # Main entry point (~200 lines)
└── cli/
    ├── __init__.py           # Group registration, shared utilities (~150 lines)
    ├── connection.py         # connection group (~300 lines)
    ├── table.py              # table group (~400 lines)
    ├── query.py              # query group (~300 lines)
    ├── session.py            # session group (~400 lines)
    ├── dashboard.py          # dashboard group (~500 lines)
    ├── knowledge.py          # knowledge group (~600 lines)
    ├── mdl.py                # mdl group (~450 lines, already exists)
    └── config.py             # config group (~200 lines)
```

**Main `cli.py` structure:**

```python
"""CLI for KAI Autonomous Agent - Intelligent Business Advisor."""

import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """KAI Autonomous Agent - AI-powered data analysis."""
    pass

# Import and register groups
from app.modules.autonomous_agent.cli.connection import connection
from app.modules.autonomous_agent.cli.table import table
from app.modules.autonomous_agent.cli.query import query
from app.modules.autonomous_agent.cli.session import session
from app.modules.autonomous_agent.cli.dashboard import dashboard
from app.modules.autonomous_agent.cli.knowledge import knowledge
from app.modules.autonomous_agent.cli.mdl import mdl
from app.modules.autonomous_agent.cli.config import config

cli.add_command(connection)
cli.add_command(table)
cli.add_command(query)
cli.add_command(session)
cli.add_command(dashboard)
cli.add_command(knowledge)
cli.add_command(mdl)
cli.add_command(config)


if __name__ == "__main__":
    cli()
```

## Complete Command Mapping

### Connection Group (6 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `create-connection` | `connection create` | cli/connection.py |
| `list-connections` | `connection list` | cli/connection.py |
| `show-connection` | `connection show` | cli/connection.py |
| `update-connection` | `connection update` | cli/connection.py |
| `delete-connection` | `connection delete` | cli/connection.py |
| `test-connection` | `connection test` | cli/connection.py |

### Table Group (5 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `list-tables` | `table list` | cli/table.py |
| `show-table` | `table show` | cli/table.py |
| `refresh-tables` | `table refresh` | cli/table.py |
| `scan-tables` | `table scan` | cli/table.py |
| `scan-all` | `table scan-all` | cli/table.py |

**Additional commands in table group:**
- `db-context` → `table context` (schema information display)
- `search-tables` → `table search` (table/column search)

### Query Group (4 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `run` | `query run` | cli/query.py |
| `interactive` | `query interactive` | cli/query.py |
| `resume` | `query resume` | cli/query.py |
| `debug-memory` | `query debug` | cli/query.py |

### Session Group (6 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `list-sessions` | `session list` | cli/session.py |
| `show-session` | `session show` | cli/session.py |
| `export-session` | `session export` | cli/session.py |
| `delete-session` | `session delete` | cli/session.py |
| `clear-sessions` | `session clear` | cli/session.py |

### Dashboard Group (7 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `create-dashboard` | `dashboard create` | cli/dashboard.py |
| `list-dashboards` | `dashboard list` | cli/dashboard.py |
| `show-dashboard` | `dashboard show` | cli/dashboard.py |
| `execute-dashboard` | `dashboard execute` | cli/dashboard.py |
| `render-dashboard` | `dashboard render` | cli/dashboard.py |
| `refine-dashboard` | `dashboard refine` | cli/dashboard.py |
| `delete-dashboard` | `dashboard delete` | cli/dashboard.py |

### Knowledge Group (24 commands)

**Glossary sub-group (5 commands):**
- `add-glossary` → `knowledge glossary add`
- `list-glossaries` → `knowledge glossary list`
- `show-glossary` → `knowledge glossary show`
- `update-glossary` → `knowledge glossary update`
- `delete-glossary` → `knowledge glossary delete`

**Instructions sub-group (5 commands):**
- `add-instruction` → `knowledge instruction add`
- `list-instructions` → `knowledge instruction list`
- `show-instruction` → `knowledge instruction show`
- `update-instruction` → `knowledge instruction update`
- `delete-instruction` → `knowledge instruction delete`

**Skills sub-group (6 commands):**
- `discover-skills` → `knowledge skill discover`
- `list-skills` → `knowledge skill list`
- `show-skill` → `knowledge skill show`
- `search-skills` → `knowledge skill search`
- `reload-skill` → `knowledge skill reload`
- `delete-skill` → `knowledge skill delete`

**Memory sub-group (8 commands):**
- `list-memories` → `knowledge memory list`
- `show-memory` → `knowledge memory show`
- `search-memories` → `knowledge memory search`
- `add-memory` → `knowledge memory add`
- `delete-memory` → `knowledge memory delete`
- `clear-memories` → `knowledge memory clear`
- `list-namespaces` → `knowledge memory namespaces`

### MDL Group (2 commands) - Already Implemented

| Old Command | New Command | File |
|------------|------------|------|
| `mdl list` | `mdl list` | cli/mdl.py (already exists) |
| `mdl show` | `mdl show` | cli/mdl.py (already exists) |

### Config Group (5 commands)

| Old Command | New Command | File |
|------------|------------|------|
| `config` | `config show` | cli/config.py |
| `env-check` | `config check` | cli/config.py |
| `version` | `config version` | cli/config.py |
| `worker` | `config worker` | cli/config.py |

## Technical Approach

### Architecture

**Shared Utilities in `cli/__init__.py`:**

```python
"""Shared CLI utilities and group registration."""

import asyncio
import click
from rich.console import Console

console = Console()

def ensure_typesense_or_prompt(required: bool = False) -> bool:
    """Check if Typesense is running, offer deployment if not."""
    # Current implementation from cli.py:247
    pass

def _run_async(coro):
    """Bridge async functions in synchronous Click context."""
    return asyncio.run(coro)

def check_typesense_running() -> bool:
    """Check if Typesense is accessible."""
    # Current implementation from cli.py:157
    pass
```

**Click Group Pattern (from MDL proof-of-concept):**

```python
# cli/connection.py
import click
from app.modules.autonomous_agent.cli import ensure_typesense_or_prompt, console, _run_async

@click.group()
def connection():
    """Database connection management commands."""
    pass

@connection.command()
@click.argument("uri")
@click.option("--alias", "-a", required=True, help="Connection alias")
def create(uri: str, alias: str):
    """Create a new database connection.

    Examples:

        kai connection create "postgresql://..." -a mydb
        kai connection create "mysql://..." -a production
    """
    if not ensure_typesense_or_prompt(required=True):
        raise click.Abort()

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    settings = Settings()
    storage = Storage(settings)
    repo = DatabaseConnectionRepository(storage)

    # Implementation...
```

### Implementation Phases

#### Phase 1: Foundation (Week 1)

**Tasks:**
1. Create `cli/` directory structure
2. Create `cli/__init__.py` with shared utilities
3. Refactor main `cli.py` to ~200 lines (router only)
4. Extract connection group to `cli/connection.py`
5. Extract config group to `cli/config.py` (simple, validates pattern)
6. Add tests for connection and config groups

**Success Criteria:**
- [ ] Groups appear in `kai --help`
- [ ] `kai connection create` works
- [ ] `kai config version` works
- [ ] Tests pass for new groups
- [ ] Old commands no longer work

#### Phase 2: Core Query Workflow (Week 2-3)

**Tasks:**
1. Extract table group to `cli/table.py`
2. Extract query group to `cli/query.py`
3. Extract session group to `cli/session.py`
4. Update cross-group dependencies (query → table → connection)
5. Test end-to-end query workflow
6. Update help text with workflow examples

**Commands to migrate:**
- Table: `list-tables`, `show-table`, `refresh-tables`, `scan-tables`, `scan-all`, `db-context`, `search-tables`
- Query: `run`, `interactive`, `resume`, `debug-memory`
- Session: `list-sessions`, `show-session`, `export-session`, `delete-session`, `clear-sessions`

**Success Criteria:**
- [ ] Complete workflow works: `connection create` → `table scan-all` → `query run` → `session list`
- [ ] All table commands work
- [ ] All query commands work
- [ ] All session commands work
- [ ] Help text guides users through workflow

#### Phase 3: Advanced Features (Week 4)

**Tasks:**
1. Extract dashboard group to `cli/dashboard.py`
2. Extract knowledge group to `cli/knowledge.py` (largest, most complex)
3. Create knowledge sub-groups (glossary, instruction, skill, memory)
4. Test all dashboard and knowledge commands
5. Performance testing (large datasets)

**Success Criteria:**
- [ ] All dashboard commands work
- [ ] All knowledge commands work (24 commands across 4 sub-groups)
- [ ] Sub-group navigation intuitive
- [ ] Performance acceptable with large datasets

#### Phase 4: Polish & Documentation (Week 5)

**Tasks:**
1. Update GETTING_STARTED.md with new command examples
2. Update all markdown files with old command references
3. Create migration guide document
4. Add shell completion support
5. Final testing and bug fixes
6. Update README and CLAUDE.md

**Success Criteria:**
- [ ] All documentation updated
- [ ] Migration guide complete
- [ ] Shell completion works
- [ ] No old command references remain

## Acceptance Criteria

### Functional Requirements

- [ ] All 59 commands successfully migrated to new group structure
- [ ] Main `cli.py` reduced to ~200 lines
- [ ] Each CLI module independently maintainable
- [ ] Query workflow works end-to-end without errors
- [ ] Help text clear and discoverable
- [ ] Error messages provide helpful guidance

### Non-Functional Requirements

- [ ] No performance regression (commands run as fast or faster)
- [ ] Test coverage maintained or improved
- [ ] Code follows existing patterns (async bridge, service initialization)
- [ ] File sizes within target ranges (200-600 lines per module)

### Quality Gates

- [ ] All existing tests pass
- [ ] New tests added for each command group
- [ ] Manual testing of all 57 commands
- [ ] End-to-end testing of core workflows
- [ ] Documentation review complete

## Breaking Changes & Migration

### Breaking Changes

**No backward compatibility** (user confirmed):

- Old commands like `kai create-connection` will not work
- Users must update scripts to use new grouped syntax
- Command-line arguments may change (e.g., `-a` → `--alias`)

### Migration Strategy

**Error Messages for Old Commands:**

Add a fallback handler in main `cli.py`:

```python
# Handle old command names with helpful error
if len(sys.argv) > 1:
    old_cmd = sys.argv[1]
    migrations = {
        "create-connection": "connection create",
        "list-connections": "connection list",
        # ... full mapping
    }
    if old_cmd in migrations:
        console.print(f"[yellow]Command moved:[/yellow]")
        console.print(f"  Old: kai {old_cmd}")
        console.print(f"  New: kai {migrations[old_cmd]}")
        console.print("\n[dim]See migration guide: https://docs.kai.ai/cli-migration[/dim]")
        sys.exit(1)
```

**Documentation Updates:**

1. Create `MIGRATION.md` with complete command mapping
2. Update GETTING_STARTED.md with all new examples
3. Update all markdown files with old command references
4. Add banner to README for 2 releases announcing breaking changes

## Dependencies & Risks

### Dependencies

- **Click 8.3.1** - Already in use, framework for CLI groups
- **Rich library** - Already in use for terminal formatting
- **Existing service layer** - No changes to services or repositories

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing user workflows | High | Clear error messages, migration guide, documentation |
| Large file extraction complexity | Medium | Work incrementally by group, test each group |
| Cross-group dependencies | Medium | Careful import ordering, shared utilities |
| Performance regression | Low | Profile before/after, optimize hot paths |
| Incomplete command mapping | Medium | Create mapping document before coding |

### Risk Mitigation

1. **Feature branch development**: Work in `feature/cli-groups` branch
2. **Incremental migration**: Implement one group at a time
3. **Comprehensive testing**: Test each group before proceeding
4. **Rollback plan**: Keep old CLI accessible in branch
5. **User communication**: Clear documentation and migration guide

## Success Metrics

- **Main cli.py**: Reduced from 4,631 to ~200 lines (95% reduction)
- **Module sizes**: All modules 200-600 lines (maintainable)
- **Test coverage**: Maintained or improved from current baseline
- **Command discoverability**: Users can find commands faster (measured by help text usage)
- **Development velocity**: Parallel development by domain possible

## Implementation Details

### Shared Utilities Pattern

**Location: `cli/__init__.py`**

```python
"""Shared CLI utilities."""

import asyncio
import click
from rich.console import Console

console = Console()

def ensure_typesense_or_prompt(required: bool = False) -> bool:
    """Check if Typesense is running, offer deployment if not.

    Args:
        required: If True, exit when Typesense not available

    Returns:
        True if Typesense is running, False otherwise
    """
    # Current implementation from cli.py:247
    # Move to shared utility for reuse across groups
    pass

def _run_async(coro):
    """Bridge async functions in synchronous Click context.

    Click commands are synchronous, but KAI services are async.
    This wrapper bridges the gap.

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of async operation
    """
    return asyncio.run(coro)

def resolve_db_identifier(identifier: str, repo):
    """Resolve database identifier (ID or alias) to connection.

    Args:
        identifier: Connection ID or database alias
        repo: DatabaseConnectionRepository instance

    Returns:
        DatabaseConnection object or None
    """
    # Try alias first
    db_conn = repo.find_by_alias(identifier)
    if db_conn:
        return db_conn

    # Try ID
    db_conn = repo.find_by_id(identifier)
    return db_conn
```

### Service Initialization Pattern

**Each command follows this pattern:**

```python
@connection.command()
@click.argument("uri")
@click.option("--alias", "-a", required=True, help="Connection alias")
def create(uri: str, alias: str):
    """Create a new database connection."""
    # 1. Check prerequisites
    if not ensure_typesense_or_prompt(required=True):
        raise click.Abort()

    # 2. Initialize services (import locally for performance)
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    # 3. Create instances
    settings = Settings()
    storage = Storage(settings)
    repo = DatabaseConnectionRepository(storage)

    # 4. Execute business logic
    try:
        # Implementation...
        console.print("[green]✔ Connection created[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
```

### Knowledge Sub-Groups Pattern

**Nested Click groups for knowledge:**

```python
# cli/knowledge.py
import click

@click.group()
def knowledge():
    """Knowledge management commands (glossary, instructions, skills, memory)."""
    pass

# Glossary sub-group
@click.group()
def glossary():
    """Business glossary management."""
    pass

@glossary.command()
@click.option("--db", "db_identifier", required=True)
@click.option("--metric", "-m", required=True)
@click.option("--sql", "-s", required=True)
def add(db_identifier: str, metric: str, sql: str):
    """Add glossary term."""
    # Implementation...

# Register sub-group
knowledge.add_command(glossary)

# Similar for instruction, skill, memory sub-groups
```

## Alternative Approaches Considered

### 1. In-Place Reorganization (Rejected)

**Description:** Keep all commands in `cli.py` but organize into Click groups with section separators.

**Pros:**
- Simpler implementation (no file splitting)
- All commands in one place

**Cons:**
- File remains ~4,600 lines (still too large)
- Difficult to navigate and maintain
- No parallel development benefit

**Why rejected:** Doesn't solve the maintainability problem.

### 2. Semi-Automated Refactoring (Rejected)

**Description:** Auto-generate groups based on existing command patterns using script detection, then manually refine.

**Pros:**
- Faster initial extraction
- Less manual work

**Cons:**
- May create awkward groupings
- Requires significant cleanup anyway
- Risk of losing context in automation

**Why rejected:** Manual extraction ensures better organization and understanding.

### 3. Flat Structure (No Sub-Groups) (Rejected)

**Description:** Create top-level groups but keep knowledge commands flat (`kai glossary add` instead of `kai knowledge glossary add`).

**Pros:**
- Fewer command levels
- Simpler namespace

**Cons:**
- 12 top-level commands (connection, table, query, session, dashboard, glossary, instruction, skill, memory, mdl, config, worker)
- Namespace pollution
- Less organized

**Why rejected:** Defeats the purpose of grouping - too many top-level commands.

## Documentation Plan

### Files to Update

1. **GETTING_STARTED.md** - All CLI examples
2. **README.md** - Quickstart examples
3. **CLAUDE.md** - CLI development patterns
4. **docs/apis/README.md** - CLI API reference
5. **docs/TROUBLESHOOTING.md** - Command examples

### New Documentation

1. **MIGRATION.md** - Complete migration guide for existing users
2. **docs/CLI_REFERENCE.md** - Auto-generated CLI reference

### Documentation Template

```markdown
## CLI Migration Guide

### Overview

The KAI CLI has been reorganized into command groups for better discoverability and maintainability.

### Command Mapping

| Old Command | New Command |
|-------------|-------------|
| `kai create-connection` | `kai connection create` |
| `kai run` | `kai query run` |
| ... | ... |

### Workflow Examples

**Before:**
\`\`\`bash
kai create-connection "postgresql://..." -a mydb
kai scan-all mydb -d
kai run "Show sales" --db mydb
\`\`\`

**After:**
\`\`\`bash
kai connection create "postgresql://..." --alias mydb
kai table scan-all mydb -d
kai query run "Show sales" --db mydb
\`\`\`

### Updating Your Scripts

1. Find all `kai ` or `kai-agent ` invocations
2. Update command names using mapping table above
3. Update option names (e.g., `-a` → `--alias`)
4. Test your scripts

### Getting Help

\`\`\`bash
kai --help              # Show all groups
kai connection --help    # Show connection commands
kai query run --help     # Show command options
\`\`\`
```

## References & Research

### Internal References

- **Current CLI**: `app/modules/autonomous_agent/cli.py` (4,631 lines)
- **MDL proof-of-concept**: `app/modules/autonomous_agent/cli.py:4197+`
- **CLI Tests**: `tests/modules/autonomous_agent/test_cli.py`
- **Analytics CLI**: `app/modules/analytics/cli.py` (separate CLI, different pattern)
- **Service Layer**: `app/modules/*/services/` (async services requiring bridge)
- **Repository Layer**: `app/modules/*/repositories/` (data access patterns)

### External References

- **Click Documentation**: https://click.palletsprojects.com/en/8.1.x/
- **Click Groups**: https://click.palletsprojects.com/en/8.1.x/commands/#nested-groups-and-compositing
- **Rich Library**: https://rich.readthedocs.io/
- **CLI Best Practices**: https://clig.dev/
- **git CLI Patterns**: https://git-scm.com/docs/git
- **docker CLI Patterns**: https://docs.docker.com/engine/reference/commandline/cli/

### Related Work

- **MDL Implementation**: `docs/brainstorms/2026-01-28-mdl-cli-commands-brainstorm.md`
- **MDL Plan**: `docs/plans/2026-01-28-feat-mdl-cli-commands-plan.md`
- **CLI Refactor Brainstorm**: `docs/brainstorms/2026-01-29-cli-refactor-groups-brainstorm.md`

### Research Findings

**Key patterns identified in codebase:**

1. **Async/Sync Bridge**: All services are async, Click is sync → use `_run_async()` wrapper
2. **Service Initialization**: Storage → Settings → Repository → Service pattern in every command
3. **Typesense Check**: `ensure_typesense_or_prompt()` used across most commands
4. **Rich Console**: Single global `console` instance for all output
5. **Error Handling**: Use `click.ClickException` for user-facing errors
6. **Identifier Resolution**: Support both UUID and alias for database connections

**Gotchas to avoid:**

1. Don't maintain backward compatibility (user confirmed breaking changes OK)
2. Don't forget async bridge in every command
3. Don't put all utilities in main CLI → extract to `cli/__init__.py`
4. Don't use tuple returns for errors → use exception hierarchy
5. Don't ignore Rich performance → limit table rows, handle overflow
6. Don't implement all groups at once → start with core query workflow

## Open Questions

### Resolved During Planning

1. **Where do `db-context` and `search-tables` go?** → table group (schema discovery activities)
2. **Should knowledge have sub-groups?** → Yes, 4 sub-groups (glossary, instruction, skill, memory)
3. **Should we add command aliases?** → No, keep structure simple
4. **Where to put shared utilities?** → `cli/__init__.py`
5. **Should we preserve help text exactly?** → No, opportunity to improve

### Still Open

1. **Should we support active connection selection?** (e.g., `kai connection use <id>` to set default)
2. **Should all commands support `--json` output?** (for scripting/automation)
3. **Should we add shell completion?** (Click supports this, but requires setup)

## Future Considerations

### Extensibility

- Easy to add new command groups (e.g., `kai alert <command>` for monitoring)
- Sub-groups can be added to existing groups
- Modular structure enables plugin architecture

### Performance Optimization

- Lazy loading of command groups (only load what's used)
- Caching of frequently accessed data
- Parallel processing for bulk operations

### User Experience Enhancements

- Interactive wizards for complex workflows
- Command aliases for power users
- Configuration file support (`~/.kai/config.yaml`)
- Shell completion and integration

## Appendix A: File Structure Template

**`cli/__init__.py` template:**

```python
"""KAI CLI shared utilities and group registration."""

import asyncio
import click
from rich.console import Console

console = Console()

def ensure_typesense_or_prompt(required: bool = False) -> bool:
    """Check if Typesense is running, offer deployment if not."""
    # Implementation...
    pass

def _run_async(coro):
    """Bridge async functions in synchronous Click context."""
    return asyncio.run(coro)

def resolve_db_identifier(identifier: str, repo):
    """Resolve database identifier (ID or alias) to connection."""
    # Implementation...
    pass
```

**`cli/connection.py` template:**

```python
"""Database connection management commands."""

import click
from app.modules.autonomous_agent.cli import ensure_typesense_or_prompt, console, _run_async

@click.group()
def connection():
    """Database connection management commands."""
    pass

@connection.command()
@click.argument("uri")
@click.option("--alias", "-a", required=True, help="Connection alias")
def create(uri: str, alias: str):
    """Create a new database connection.

    Examples:

        kai connection create "postgresql://..." -a mydb
        kai connection create "mysql://..." -a production
    """
    if not ensure_typesense_or_prompt(required=True):
        raise click.Abort()

    # Implementation...
    pass

# ... other connection commands
```

## Appendix B: Test Template

**`tests/modules/autonomous_agent/cli/test_connection.py` template:**

```python
"""Tests for connection CLI group."""

from click.testing import CliRunner
from app.modules.autonomous_agent.cli.connection import connection

def test_connection_help():
    """Test connection group help."""
    runner = CliRunner()
    result = runner.invoke(connection, ["--help"])
    assert result.exit_code == 0
    assert "Database connection management" in result.output

def test_connection_create_help():
    """Test connection create help."""
    runner = CliRunner()
    result = runner.invoke(connection, ["create", "--help"])
    assert result.exit_code == 0
    assert "--alias" in result.output

def test_connection_create_with_uri(monkeypatch_typesense):
    """Test connection create with valid URI."""
    # Mock Typesense and services
    runner = CliRunner()
    result = runner.invoke(connection, [
        "create",
        "postgresql://user:pass@localhost:5432/db",
        "--alias", "testdb"
    ])
    assert result.exit_code == 0
    assert "Connection created" in result.output
```
