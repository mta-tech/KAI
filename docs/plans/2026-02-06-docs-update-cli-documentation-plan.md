---
title: Update CLI Documentation in README.md and CLAUDE.md
type: docs
date: 2026-02-06
---

# Update CLI Documentation in README.md and CLAUDE.md

## Overview

Update the CLI documentation in README.md (lines 453-578) and CLAUDE.md (lines 95-112) to reflect the completed CLI refactor from flat commands to grouped commands. The refactor was completed on 2026-01-29 (commits M1-E1-S1 through M1-E3-S8) and reorganized 59 flat commands into 8 logical groups with 58+ commands.

## Problem Statement

User-facing documentation uses the old flat CLI syntax (`kai create-connection`, `kai scan-all`, `kai run`) while the actual CLI now uses grouped syntax (`kai connection create`, `kai table scan-all`, `kai query run`). This causes confusion for new users following the README tutorial.

Additionally, several command groups are completely undocumented in README.md: dashboard, knowledge (with 4 sub-groups), mdl, config, and session management.

CLAUDE.md also references the wrong entry point path (`cli.py` instead of `main.py`).

## Acceptance Criteria

- [x] README.md CLI section uses correct grouped command syntax
- [x] README.md Quick Tutorial workflow uses new syntax
- [x] README.md documents all 8 command groups with examples
- [x] README.md includes common workflow patterns
- [x] CLAUDE.md CLI section uses correct grouped command syntax
- [x] CLAUDE.md references correct entry point (`app/modules/autonomous_agent/main.py`)
- [x] No old flat command syntax remains in either file
- [x] Documentation style matches existing README conventions (no emoji, professional tone, bash code blocks)

## MVP

### Task 1: Update README.md CLI Section (lines 453-578)

Replace the entire CLI section (`## CLI Usage` through the `---` before `## Environment Configuration`) with updated content.

**Structure of new section:**

```markdown
## CLI Usage

[Intro paragraph - keep existing]

### Quick CLI Tutorial

[Updated 4-step workflow with new grouped syntax]

### Command Reference

[Command tree showing all 8 groups]
[Table or code block for each group with key commands]

### Common Workflows

[2-3 workflow examples: setup, knowledge, dashboard]

### Advanced CLI Features

[Updated examples with new syntax]
```

**Specific changes in README.md:**

1. **Quick Tutorial** — Update all commands:
   - `kai create-connection` → `kai connection create`
   - `kai scan-all` → `kai table scan-all`
   - `kai run` → `kai query run`
   - `kai interactive` → `kai query interactive`

2. **Available Commands** — Replace flat command list with grouped structure:
   ```
   kai config       # Configuration and system utilities
   kai connection   # Database connection management
   kai table        # Table management and schema scanning
   kai query        # Query execution and interactive sessions
   kai session      # Session management
   kai dashboard    # Dashboard creation and management
   kai knowledge    # Knowledge management (glossary, instructions, skills, memory)
   kai mdl          # Semantic layer (MDL) management
   ```
   Then show key commands per group.

3. **Advanced Features** — Update:
   - `kai add-instruction` → `kai knowledge instruction add`
   - Add dashboard creation example
   - Add session export example

4. **Common Workflows** — New subsection with:
   - Setup workflow (connection → scan → query)
   - Knowledge workflow (glossary → instruction → query)
   - Dashboard workflow (create → execute → render)

### Task 2: Update CLAUDE.md CLI Section (lines 95-112)

Replace lines 95-112 with updated content:

1. **Fix command syntax** — All examples use grouped syntax
2. **Fix entry point** — `app/modules/autonomous_agent/cli.py` → `app/modules/autonomous_agent/main.py`
3. **Add command group overview** — Brief list of all 8 groups
4. **Keep developer-focused tone** — Concise, code-heavy style matching rest of CLAUDE.md

**New CLAUDE.md CLI section structure:**

```markdown
## CLI Commands

```bash
# List CLI commands
uv run kai --help

# Database management
uv run kai connection create "postgresql://user:pass@host:5432/db" -a mydb
uv run kai table scan-all mydb -d  # Scan with AI descriptions

# Interactive session
uv run kai query interactive --db mydb

# One-shot analysis
uv run kai query run "Analyze sales by region" --db mydb
```

CLI entry point: `app/modules/autonomous_agent/main.py` (registered as `kai` in pyproject.toml).

Command groups: `config`, `connection`, `table`, `query`, `session`, `dashboard`, `knowledge` (sub-groups: `glossary`, `instruction`, `skill`, `memory`), `mdl`.
```

### Task 3: Verify Table of Contents

README.md line 27 has `[CLI Usage & Tutorial](#cli-usage)`. If the section heading changes, update the ToC anchor. Current heading `## CLI Usage` generates anchor `#cli-usage`, so this should remain compatible. Verify after edit.

## References

- Brainstorm: `docs/brainstorms/2026-02-06-cli-documentation-update-brainstorm.md`
- Refactor plan: `docs/plans/2026-01-29-refactor-cli-groups-plan.md`
- Verification report: `docs/verification/2026-01-29-cli-refactor-phase3-verification.md`
- CLI entry point: `app/modules/autonomous_agent/main.py`
- CLI modules: `app/modules/autonomous_agent/cli/*.py`
