# CLI Reference

KAI provides a powerful command-line interface organized into logical command groups for database management, knowledge curation, and natural language analysis.

## Command Groups

```
kai
├── config              # Configuration and system utilities
├── connection          # Database connection management
├── table               # Table management and schema scanning
├── query               # Query execution and interactive sessions
├── session             # Session management and export
├── dashboard           # Dashboard creation and management
├── knowledge           # Knowledge management
│   ├── glossary        #   Business metric definitions
│   ├── instruction     #   SQL generation rules
│   ├── skill           #   Reusable analysis patterns
│   └── memory          #   Long-term memory store
├── context             # Context asset management
└── benchmark           # Benchmark execution and results
```

## Quick Start Tutorial

### Step 1: Connect to your database

```bash
# PostgreSQL
uv run kai connection create \
  "postgresql://user:password@localhost:5432/sales_db" \
  -a sales

# MySQL
uv run kai connection create \
  "mysql://user:password@localhost:3306/crm_db" \
  -a crm

# SQLite
uv run kai connection create \
  "sqlite:///path/to/database.db" \
  -a local_db
```

### Step 2: Scan your database schema

```bash
# With AI-generated descriptions (recommended)
uv run kai table scan-all sales -d
```

### Step 3: Run your first query

```bash
uv run kai query run "Show total sales by month for 2024" --db sales
```

### Step 4: Interactive mode

```bash
uv run kai query interactive --db sales
```

## Help

```bash
kai --help                                 # Show all command groups
kai <group> --help                         # Group-specific help
kai <group> <command> --help               # Command-specific help
```

## Command Details

| Group | Commands |
|-------|----------|
| [Connection](connection.md) | `create`, `list`, `show`, `test`, `update`, `delete` |
| [Query](query.md) | `run`, `interactive`, `resume` |
| [Context](context.md) | `list`, `show`, `create`, `update`, `delete`, `promote`, `deprecate`, `search`, `tags` |
| [Benchmark](benchmark.md) | `run`, `list`, `info`, `results` |
