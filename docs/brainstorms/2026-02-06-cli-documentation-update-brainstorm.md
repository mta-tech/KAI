# Brainstorm: CLI Documentation Update

**Date:** 2026-02-06
**Status:** Approved

## What We're Building

A full documentation update across README.md and CLAUDE.md to reflect the recently completed CLI refactor (flat commands -> grouped commands). The CLI now has 8 command groups with 58+ commands, but user-facing docs still show the old syntax.

## Why This Approach

The CLI refactor (completed 2026-01-29, commits M1-E1-S1 through M1-E3-S8) reorganized 59 flat commands into 8 logical groups. Documentation must match the current implementation to avoid user confusion.

**Inline-only approach** chosen over creating a separate CLI_REFERENCE.md to avoid file sprawl. README.md serves users, CLAUDE.md serves developers/AI agents.

## Key Decisions

1. **Scope**: Full update of both README.md and CLAUDE.md
2. **No separate CLI reference file**: Keep everything inline in existing docs
3. **README.md strategy**: Comprehensive CLI section with command tree, workflow examples, and common patterns for all 8 groups
4. **CLAUDE.md strategy**: Update CLI section with correct grouped syntax, entry point reference, and developer-relevant patterns
5. **Coverage**: All 8 command groups documented: config, connection, table, query, session, dashboard, knowledge, mdl
6. **Workflows**: Include common workflow patterns (setup, knowledge, dashboard, session management)

## What Changed in the Refactor

### Old Syntax (pre-refactor)
```bash
kai create-connection ...
kai list-connections
kai scan-all ...
kai run ...
kai interactive ...
kai add-instruction ...
```

### New Syntax (current)
```bash
kai connection create ...
kai connection list
kai table scan-all ...
kai query run ...
kai query interactive ...
kai knowledge instruction add ...
```

### Command Group Structure
```
kai
├── config       (4 commands)
├── connection   (6 commands)
├── table        (7 commands)
├── query        (4 commands)
├── session      (5 commands)
├── dashboard    (7 commands)
├── knowledge    (23 commands, 4 sub-groups)
│   ├── glossary     (5)
│   ├── instruction  (5)
│   ├── skill        (6)
│   └── memory       (7)
└── mdl          (2 commands)
```

## Open Questions

None - requirements are clear.
