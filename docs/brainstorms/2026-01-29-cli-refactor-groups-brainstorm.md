# KAI CLI Refactor - Command Groups

**Date:** 2026-01-29
**Status:** Draft
**Related Issue:** TBD

---

## What We're Building

Refactor the KAI CLI from a flat 59-command structure to organized domain-based groups, improving discoverability, reducing code complexity, and enhancing user experience.

**Current State:**
- 59 commands in a flat structure
- 4,631 lines in a single `cli.py` file
- MDL group already implemented as proof-of-concept

**Target State:**
- Domain-based command groups (connection, table, query, session, dashboard, knowledge, system)
- Modular CLI files split by domain
- Breaking changes (no backward compatibility)

## Why This Approach

**User Requirements:**
- Primary goal: Improve discoverability, reduce complexity, AND improve UX (all of the above)
- Query workflow is the highest priority for daily users
- Full refactor scope (not incremental)
- Breaking changes acceptable

**Chosen Approach:** Modular CLI files with Click groups

This approach:
- Follows Click framework best practices
- Reduces main `cli.py` from 4,631 to ~200 lines
- Each module ~200-400 lines (maintainable)
- Enables parallel development by domain
- Improves testability per module
- Follows patterns already established by MDL group

## Key Decisions

### 1. Command Group Structure

**Domain-based groups (8 groups total):**

```bash
kai connection <command>      # Database connection management
kai table <command>           # Table/schema management  
kai query <command>           # Query execution and analysis
kai session <command>         # Conversation session management
kai dashboard <command>       # Dashboard management
kai knowledge <command>       # Glossary, instructions, skills, memory
kai mdl <command>             # MDL semantic layer (already exists)
kai config <command>          # Configuration and system utilities
```

**Rationale:** Groups commands by user intent and domain. Query workflow (connection → table → query → session) is the primary user journey.

### 2. File Organization

**Modular CLI structure:**

```
app/modules/autonomous_agent/
├── cli.py                    # Main entry point (~200 lines)
└── cli/
    ├── __init__.py           # Group registration
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
@click.group()
def cli():
    """KAI Autonomous Agent - AI-powered data analysis."""
    pass

# Import and register groups
from app.modules.autonomous_agent.cli.connection import connection
from app.modules.autonomous_agent.cli.table import table
# ... etc

cli.add_command(connection)
cli.add_command(table)
# ... etc
```

**Rationale:** Each module is independently maintainable, testable, and can be developed in parallel. Main CLI becomes a simple router.

### 3. Command Mapping

**Current → New mapping:**

#### Connection Group (6 commands)
```
create-connection    → connection create
list-connections     → connection list
show-connection      → connection show
update-connection    → connection update
delete-connection    → connection delete
test-connection      → connection test
```

#### Table Group (5 commands)
```
list-tables          → table list [--db <id>]
show-table           → table show <table_id>
refresh-tables       → table refresh [--db <id>]
scan-tables          → table scan [--db <id>] [--with-descriptions]
scan-all             → table scan-all [--db <id>] [--with-descriptions] [--generate-mdl]
```

#### Query Group (4 commands)
```
run                  → query run <prompt> --db <id>
interactive          → query interactive --db <id>
resume               → query resume <session_id>
debug-memory         → query debug <session_id>
```

#### Session Group (6 commands)
```
list-sessions        → session list [--db <id>]
show-session         → session show <session_id>
export-session       → session export <session_id> -o <file>
delete-session       → session delete <session_id>
clear-sessions       → session clear [--db <id>]
```

#### Dashboard Group (6 commands)
```
create-dashboard     → dashboard create <request> --db <id>
list-dashboards      → dashboard list --db <id>
show-dashboard       → dashboard show <dashboard_id>
execute-dashboard    → dashboard execute <dashboard_id>
render-dashboard     → dashboard render <dashboard_id> -f <format>
refine-dashboard     → dashboard refine <dashboard_id> <request>
delete-dashboard     → dashboard delete <dashboard_id>
```

#### Knowledge Group (24 commands)
```
# Glossary (5)
add-glossary         → knowledge glossary add
list-glossaries      → knowledge glossary list
show-glossary        → knowledge glossary show
update-glossary      → knowledge glossary update
delete-glossary      → knowledge glossary delete

# Instructions (5)
add-instruction      → knowledge instruction add
list-instructions    → knowledge instruction list
show-instruction     → knowledge instruction show
update-instruction   → knowledge instruction update
delete-instruction   → knowledge instruction delete

# Skills (6)
discover-skills       → knowledge skill discover
list-skills          → knowledge skill list
show-skill           → knowledge skill show
search-skills        → knowledge skill search
reload-skill         → knowledge skill reload
delete-skill         → knowledge skill delete

# Memory (8)
list-memories        → knowledge memory list
show-memory          → knowledge memory show
search-memories      → knowledge memory search
add-memory           → knowledge memory add
delete-memory        → knowledge memory delete
clear-memories       → knowledge memory clear
list-namespaces      → knowledge memory namespaces
```

#### MDL Group (2 commands) - Already implemented
```
mdl list             → mdl list [--db <id>]
mdl show             → mdl show <id>
```

#### Config Group (4 commands)
```
config               → config show
env-check            → config check
version              → config version
```

**Rationale:** Consistent naming pattern (group verb) and flat verb structure within groups. No nested sub-groups.

### 4. Implementation Priority

**Phase 1: Core Query Workflow (MVP)**
1. Connection group (prerequisite)
2. Table group (schema discovery)
3. Query group (primary user activity)
4. Session group (conversation management)

**Phase 2: Advanced Features**
5. Dashboard group (visualization)
6. Knowledge group (business logic + memory)
7. Config group (utilities)

**Phase 3: Polish**
8. Update documentation
9. Add tests
10. Update examples in README

**Rationale:** Query workflow is the primary user journey. Implement this end-to-end first to validate the pattern.

### 5. Breaking Changes

**No backward compatibility** (user confirmed):

- Old commands like `kai create-connection` will not work
- Users must update scripts to use new grouped syntax
- Migration guide in documentation

**Mitigation:**
- Clear error message: "Command moved. Try: kai connection create"
- Update all documentation with new examples
- Release notes with migration guide

**Rationale:** Simpler codebase, no dual-maintenance burden, cleaner user experience long-term.

### 6. Validation Strategy

**Tests after refactor** (user confirmed):

1. Implement grouped commands
2. Add pytest tests for each command group
3. Manual testing of core workflows
4. Update CLI examples in docs

**Test coverage:**
- Unit tests per CLI module
- Integration tests for query workflow
- End-to-end tests for critical paths

**Rationale:** Tests validate new structure rather than old patterns.

## Open Questions

1. **Should `db-context` and `search-tables` be in `table` group or `query` group?**
   - `db-context` shows schema → table group?
   - `search-tables` finds tables → table group?
   - Or both in query group as pre-query activities?

2. **Should knowledge group have sub-groups?**
   - Current: `kai knowledge glossary add`
   - Alternative: `kai glossary add`, `kai instruction add` (flat)
   - Trade-off: Namespace hierarchy vs. fewer top-level commands

3. **Should we add command aliases for common workflows?**
   - Example: `kai scan` as alias for `kai table scan-all`?
   - Could improve UX but adds complexity

4. **How to handle command-specific shared utilities?**
   - `ensure_typesense_or_prompt()` used in many commands
   - `_run_async()` bridge function
   - Keep in `cli/__init__.py` or shared utility module?

5. **Should we preserve existing help text and examples exactly?**
   - Opportunity to improve documentation
   - Risk of losing context/usage patterns

## Decided During Brainstorm

- ✅ Goal: All improvements (discoverability, complexity, UX)
- ✅ Scope: Full refactor (not incremental)
- ✅ Priority: Query workflow (connection → table → query → session)
- ✅ Structure: Domain-based groups (8 groups)
- ✅ File organization: Modular CLI files split by domain
- ✅ Backward compatibility: Breaking changes (no aliases)
- ✅ Validation: Tests after refactor
- ✅ Approach: Modular groups with Click framework

## Examples

**Before (flat structure):**
```bash
# Setup workflow
kai create-connection "postgresql://..." -a mydb
kai scan-all mydb -d --generate-mdl

# Query workflow
kai run "Show sales by month" --db mydb
kai interactive --db mydb
kai list-sessions --db mydb
```

**After (grouped structure):**
```bash
# Setup workflow
kai connection create "postgresql://..." -a mydb
kai table scan-all mydb -d --generate-mdl

# Query workflow
kai query run "Show sales by month" --db mydb
kai query interactive --db mydb
kai session list --db mydb
```

**Knowledge management (before):**
```bash
kai add-glossary mydb --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"
kai add-instruction mydb -c "Always" -r "Format currency"
kai list-memories mydb
```

**Knowledge management (after):**
```bash
kai knowledge glossary add mydb --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"
kai knowledge instruction add mydb -c "Always" -r "Format currency"
kai knowledge memory list mydb
```

## Next Steps

1. Implement Phase 1: Connection + Table + Query + Session groups
2. Write tests for new command structure
3. Update documentation with new command examples
4. Implement Phase 2: Dashboard + Knowledge + Config groups
5. Final validation and polish

## References

- Current CLI: `app/modules/autonomous_agent/cli.py` (4,631 lines)
- MDL group implementation: `app/modules/autonomous_agent/cli.py` (lines 4197+)
- Click documentation: https://click.palletsprojects.com/
- CLI patterns from: git, docker, kubectl
