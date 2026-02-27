# Connection CLI

Manage database connections.

## Commands

### Create Connection

```bash
kai connection create <uri> -a <alias>
```

**Examples:**

```bash
# PostgreSQL
kai connection create "postgresql://user:pass@host:5432/db" -a sales

# MySQL
kai connection create "mysql://user:pass@host:3306/db" -a crm

# SQLite
kai connection create "sqlite:///path/to/database.db" -a local

# BigQuery
kai connection create "bigquery://project/dataset" -a bq_analytics
```

### List Connections

```bash
kai connection list
```

### Show Connection Details

```bash
kai connection show <id_or_alias>
```

### Test Connection

```bash
kai connection test <uri>
```

Test without saving to verify credentials and connectivity.

### Update Connection

```bash
kai connection update <id> --alias <new_alias>
```

### Delete Connection

```bash
kai connection delete <id> [-f]
```

Use `-f` to skip confirmation prompt.
