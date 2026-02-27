# Context CLI

Context asset commands for managing knowledge artifacts.

## Commands

### List Context Assets

```bash
kai context list --db <connection_id> [--type <type>] [--state <state>] [--limit <n>]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--db, -d` | Database connection ID or alias (required) |
| `--type` | Filter by asset type: `table_description`, `glossary`, `instruction`, `skill` |
| `--state` | Filter by lifecycle state: `draft`, `verified`, `published`, `deprecated` |
| `--limit` | Maximum number of results (default: 50) |

**Example:**

```bash
kai context list --db sales --type instruction --state published
```

### Create Context Asset

```bash
kai context create --db <connection_id> --type <type> --key <key> --name <name> --content '<json>'
```

**Example:**

```bash
kai context create \
  --db sales \
  --type instruction \
  --key revenue_analysis \
  --name "Revenue Analysis Rules" \
  --content '{"rules": ["Always filter by active status", "Use USD currency"]}'
```

### Show Context Asset

```bash
kai context show <asset_id>
```

### Update Context Asset

```bash
kai context update <asset_id> [--name <name>] [--content '<json>'] [--tags <tags>]
```

### Promote Context Asset

```bash
kai context promote <asset_id> <target_state> --by "<author>" [--note "<note>"]
```

**Target states:** `verified`, `published`

**Example:**

```bash
kai context promote asset_123 verified --by "Jane Doe" --note "Reviewed and approved"
```

### Deprecate Context Asset

```bash
kai context deprecate <asset_id> --by "<author>" --reason "<reason>"
```

### Delete Context Asset

```bash
kai context delete <db_connection_id> <asset_type> <canonical_key> [--version <version>] [--force]
```

### Search Context Assets

```bash
kai context search --db <connection_id> --query "<query>" [--limit <n>]
```

**Example:**

```bash
kai context search --db sales --query "revenue calculation" --limit 10
```

### List Tags

```bash
kai context tags [--category <category>]
```

## Asset Types

| Type | Description |
|------|-------------|
| `table_description` | Descriptive metadata about database tables |
| `glossary` | Business terminology and definitions |
| `instruction` | Domain-specific analysis instructions |
| `skill` | Reusable analysis patterns and templates |

## Lifecycle States

| State | Description |
|-------|-------------|
| `draft` | Initial creation, not yet verified |
| `verified` | Validated by domain expert |
| `published` | Approved for reuse across missions |
| `deprecated` | Superseded or no longer relevant |
