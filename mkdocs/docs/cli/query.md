# Query CLI

Execute natural language queries against your databases.

## Commands

### One-shot Query

```bash
kai query run "<question>" --db <connection_id>
```

**Options:**

| Option | Description |
|--------|-------------|
| `--db` | Database connection ID or alias (required) |
| `--mode` | Query mode: `analysis`, `query`, `script`, `full_autonomy` |

**Examples:**

```bash
kai query run "Show total sales by month for 2024" --db sales
kai query run "List top 10 customers by revenue" --db sales
kai query run "Analyze correlation between price and quantity sold" --db sales
```

### Interactive Session

```bash
kai query interactive --db <connection_id>
```

Start an interactive conversation with your data:

```
> Show me total revenue this quarter
> Which products are underperforming?
> Create a forecast for next month's sales
> What's the average order value by customer segment?
> exit
```

### Resume Session

```bash
kai query resume <session_id> "<follow-up>" --db <connection_id>
```

Continue a previous conversation:

```bash
kai query resume sess_123 "Break it down by region" --db sales
```

## Query Modes

| Mode | Description |
|------|-------------|
| `analysis` | Focus on data analysis and insights |
| `query` | Direct SQL query generation |
| `script` | Generate executable scripts |
| `full_autonomy` | Complete autonomous analysis (default) |

## Tips

1. **Be specific** - Include column names, time periods, and filters
2. **Use business terms** - KAI understands glossary definitions
3. **Ask follow-ups** - Build on previous results in interactive mode
4. **Export results** - Use session export for documentation
