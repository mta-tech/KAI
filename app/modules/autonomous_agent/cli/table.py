"""Table management commands for KAI Autonomous Agent.

This module provides commands for managing database tables:
- List and search tables
- Scan tables to extract schema metadata
- Refresh table list from database
- Show detailed table information
- Load database context for AI analysis
"""
import json
import re
from urllib.parse import urlparse

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.modules.autonomous_agent.cli import (
    _run_async,
    console,
    ensure_typesense_or_prompt,
)

# ============================================================================
# Table Command Group
# ============================================================================

@click.group()
def table():
    """Table management commands - scan, list, search, and inspect database tables."""
    pass


# ============================================================================
# List Tables
# ============================================================================

@table.command("list")
@click.argument("db_connection_id")
@click.option("--schema", "-s", help="Filter by schema")
@click.option("--status", type=click.Choice(["all", "scanned", "not_scanned", "failed"]), default="all", help="Filter by scan status")
@click.option("--verbose", "-v", is_flag=True, help="Show full descriptions and column counts")
@click.option("--columns", "-c", is_flag=True, help="Show column names for each table")
def list_tables(db_connection_id: str, schema: str, status: str, verbose: bool, columns: bool):
    """List tables for a database connection.

    Examples:

        kai table list abc123

        kai table list abc123 --schema public

        kai table list abc123 --status not_scanned

        kai table list abc123 --verbose

        kai table list abc123 --columns
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository

    if not ensure_typesense_or_prompt():
        return

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Get tables
    filter_dict = {"db_connection_id": db_connection_id}
    if schema:
        filter_dict["db_schema"] = schema

    tables = table_repo.find_by(filter_dict)

    # Filter by status
    if status != "all":
        status_map = {
            "scanned": "SCANNED",
            "not_scanned": "NOT_SCANNED",
            "failed": "FAILED"
        }
        tables = [t for t in tables if t.sync_status == status_map.get(status)]

    if not tables:
        console.print("[yellow]No tables found[/yellow]")
        return

    console.print(f"[bold]Tables for '{db_connection.alias}' ({len(tables)} total):[/bold]\n")

    # Group by schema
    schemas = {}
    for table in tables:
        if table.db_schema not in schemas:
            schemas[table.db_schema] = []
        schemas[table.db_schema].append(table)

    for schema_name, schema_tables in schemas.items():
        console.print(f"[cyan]Schema: {schema_name}[/cyan]")
        for table in schema_tables:
            status_icon = {
                "SCANNED": "[green]✔[/green]",
                "NOT_SCANNED": "[yellow]○[/yellow]",
                "SYNCHRONIZING": "[blue]⟳[/blue]",
                "FAILED": "[red]✖[/red]",
                "DEPRECATED": "[dim]⊘[/dim]"
            }.get(table.sync_status, "[dim]?[/dim]")

            col_count = f" ({len(table.columns)} cols)" if table.columns else ""

            console.print(f"\n  {status_icon} [bold]{table.table_name}[/bold]{col_count}")
            console.print(f"      [dim]ID: {table.id}[/dim]")

            # Show description
            if table.table_description:
                if verbose:
                    console.print(f"      [italic]{table.table_description}[/italic]")
                else:
                    desc = table.table_description[:80] + "..." if len(table.table_description) > 80 else table.table_description
                    console.print(f"      [italic]{desc}[/italic]")

            # Show columns if requested
            if columns and table.columns:
                col_names = [f"[cyan]{c.name}[/cyan]" for c in table.columns[:10]]
                more = f" +{len(table.columns) - 10} more" if len(table.columns) > 10 else ""
                console.print(f"      Columns: {', '.join(col_names)}{more}")


# ============================================================================
# Show Table
# ============================================================================

@table.command("show")
@click.argument("table_id")
def show_table(table_id: str):
    """Show detailed information about a table.

    Example:

        kai table show table_abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.table_description.repositories import TableDescriptionRepository

    if not ensure_typesense_or_prompt():
        return

    storage = Storage(Settings())
    table_repo = TableDescriptionRepository(storage)

    table = table_repo.find_by_id(table_id)

    if not table:
        console.print(f"[red]Error:[/red] Table '{table_id}' not found")
        return

    # Build info panel
    info_lines = [
        f"[bold]ID:[/bold] {table.id}",
        f"[bold]Table:[/bold] {table.db_schema}.{table.table_name}",
        f"[bold]Connection ID:[/bold] {table.db_connection_id}",
        f"[bold]Status:[/bold] {table.sync_status}",
        f"[bold]Last Sync:[/bold] {table.last_sync or 'Never'}",
    ]

    if table.table_description:
        info_lines.append(f"\n[bold]Description:[/bold]\n{table.table_description}")

    console.print(Panel("\n".join(info_lines), title=f"Table: {table.table_name}", border_style="cyan"))

    # Show columns
    if table.columns:
        console.print(f"\n[bold]Columns ({len(table.columns)}):[/bold]")
        for col in table.columns:
            pk_marker = " [yellow]PK[/yellow]" if col.is_primary_key else ""
            fk_marker = f" [blue]FK→{col.foreign_key.reference_table}[/blue]" if col.foreign_key else ""
            card_marker = " [dim](low cardinality)[/dim]" if col.low_cardinality else ""

            console.print(f"  • [cyan]{col.name}[/cyan] ({col.data_type}){pk_marker}{fk_marker}{card_marker}")
            if col.description:
                console.print(f"    [dim]{col.description}[/dim]")
            if col.categories:
                console.print(f"    [dim]Values: {', '.join(str(c) for c in col.categories[:5])}{' ...' if len(col.categories) > 5 else ''}[/dim]")

    # Show examples
    if table.examples:
        console.print(f"\n[bold]Sample Data ({len(table.examples)} rows):[/bold]")
        for i, example in enumerate(table.examples[:3]):
            console.print(f"  Row {i+1}: {example}")

    # Show schema DDL
    if table.table_schema:
        console.print(f"\n[bold]Schema (DDL):[/bold]")
        console.print(Panel(table.table_schema, border_style="dim"))


# ============================================================================
# Refresh Tables
# ============================================================================

@table.command("refresh")
@click.argument("db_connection_id")
def refresh_tables(db_connection_id: str):
    """Refresh the table list from database.

    This command syncs the table list with the actual database,
    adding new tables and marking removed ones as deprecated.

    Example:

        kai table refresh abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.table_description.services import TableDescriptionService

    if not ensure_typesense_or_prompt():
        return

    settings = Settings()
    storage = Storage(settings)
    service = TableDescriptionService(storage)

    console.print(f"[bold]Refreshing tables for connection '{db_connection_id}'...[/bold]")

    try:
        with console.status("[bold cyan]Syncing with database...[/bold cyan]"):
            tables = service.refresh_table_description(db_connection_id)

        # Count by status
        new_tables = [t for t in tables if t.sync_status == "NOT_SCANNED"]
        deprecated = [t for t in tables if t.sync_status == "DEPRECATED"]

        console.print(f"\n[green]✔ Refresh complete![/green]")
        console.print(f"  Total tables: {len(tables)}")
        if new_tables:
            console.print(f"  [cyan]New tables:[/cyan] {len(new_tables)}")
            for t in new_tables[:5]:
                console.print(f"    + {t.db_schema}.{t.table_name}")
            if len(new_tables) > 5:
                console.print(f"    [dim]... and {len(new_tables) - 5} more[/dim]")
        if deprecated:
            console.print(f"  [yellow]Deprecated:[/yellow] {len(deprecated)}")
            for t in deprecated[:5]:
                console.print(f"    - {t.db_schema}.{t.table_name}")

    except Exception as e:
        console.print(f"\n[red]✖ Refresh failed:[/red] {str(e)}")


# ============================================================================
# Scan Tables
# ============================================================================

@table.command("scan")
@click.argument("db_connection_id")
@click.option("--table", "-t", "table_ids", multiple=True, help="Specific table IDs to scan (can specify multiple)")
@click.option("--with-descriptions", "-d", is_flag=True, help="Generate AI descriptions for tables and columns")
@click.option("--model-family", default="google", help="LLM model family (openai, google, ollama)")
@click.option("--model-name", default="gemini-2.5-flash", help="LLM model name")
@click.option("--instruction", "-i", type=str, help="Custom instruction for description generation")
def scan_tables(db_connection_id: str, table_ids: tuple, with_descriptions: bool, model_family: str, model_name: str, instruction: str):
    """Scan database tables to extract schema metadata.

    This command scans tables to extract column information, data types,
    cardinality, and sample data. Optionally generates AI descriptions.

    Examples:

        # Scan all tables for a connection
        kai table scan abc123

        # Scan specific tables
        kai table scan abc123 -t table_id_1 -t table_id_2

        # Scan with AI-generated descriptions
        kai table scan abc123 --with-descriptions

        # Use specific LLM for descriptions
        kai table scan abc123 -d --model-family openai --model-name gpt-4o
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.modules.sql_generation.models import LLMConfig
    from app.utils.sql_database.scanner import SqlAlchemyScanner

    if not ensure_typesense_or_prompt():
        return

    settings = Settings()
    storage = Storage(settings)
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)
    scanner = SqlAlchemyScanner()

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Get tables to scan
    if table_ids:
        tables_to_scan = [table_repo.find_by_id(tid) for tid in table_ids]
        tables_to_scan = [t for t in tables_to_scan if t is not None]
    else:
        tables_to_scan = table_repo.find_by({"db_connection_id": db_connection_id})

    if not tables_to_scan:
        console.print("[yellow]No tables found to scan[/yellow]")
        return

    console.print(f"[bold]Scanning {len(tables_to_scan)} tables for '{db_connection.alias}'...[/bold]")
    if with_descriptions:
        console.print(f"[dim]AI descriptions enabled ({model_family}/{model_name})[/dim]")

    # Configure LLM if descriptions requested
    llm_config = None
    if with_descriptions:
        llm_config = LLMConfig(
            model_family=model_family,
            model_name=model_name,
        )

    # Group by schema
    db_connection_service = DatabaseConnectionService(scanner, storage)

    try:
        schemas_processed = set()
        for table in tables_to_scan:
            schema = table.db_schema
            if schema in schemas_processed:
                continue
            schemas_processed.add(schema)

            schema_tables = [t for t in tables_to_scan if t.db_schema == schema]
            console.print(f"\n[cyan]Schema: {schema}[/cyan] ({len(schema_tables)} tables)")

            with console.status(f"[bold cyan]Scanning {schema}...[/bold cyan]"):
                database = db_connection_service.get_sql_database(db_connection, schema)
                scanner.scan(
                    database.engine,
                    schema_tables,
                    table_repo,
                    llm_config,
                    instruction or ""
                )

            for t in schema_tables:
                console.print(f"  [green]✔[/green] {t.table_name}")

        console.print(f"\n[green]✔ Scanning complete![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Scanning failed:[/red] {str(e)}")


# ============================================================================
# Scan All Tables
# ============================================================================

@table.command("scan-all")
@click.argument("db_connection_id")
@click.option("--with-descriptions", "-d", is_flag=True, help="Generate AI descriptions for tables and columns")
@click.option("--model-family", default="google", help="LLM model family (openai, google, ollama)")
@click.option("--model-name", default="gemini-2.5-flash", help="LLM model name")
@click.option("--instruction", "-i", type=str, help="Custom instruction for description generation")
@click.option("--refresh/--no-refresh", default=True, help="Refresh table list from database first")
@click.option("--generate-mdl", "-m", is_flag=True, help="Generate MDL semantic layer manifest after scan")
@click.option("--mdl-name", type=str, help="Name for generated MDL manifest (default: auto-generated)")
def scan_all(db_connection_id: str, with_descriptions: bool, model_family: str, model_name: str, instruction: str, refresh: bool, generate_mdl: bool, mdl_name: str):
    """Scan ALL tables in a database connection.

    This is a convenience command that:
    1. Refreshes the table list from the database (optional)
    2. Scans all tables to extract schema metadata
    3. Optionally generates AI descriptions
    4. Optionally generates MDL semantic layer manifest

    Examples:

        # Scan all tables
        kai table scan-all abc123

        # Scan all with AI descriptions
        kai table scan-all abc123 --with-descriptions

        # Skip refresh, just scan existing tables
        kai table scan-all abc123 --no-refresh

        # Use OpenAI for descriptions
        kai table scan-all abc123 -d --model-family openai --model-name gpt-4o

        # Generate MDL semantic layer after scan
        kai table scan-all abc123 --generate-mdl

        # Generate MDL with custom name
        kai table scan-all abc123 -m --mdl-name "Sales Analytics"

        # Full scan with descriptions and MDL generation
        kai table scan-all abc123 -d -m --mdl-name "E-Commerce Semantic Layer"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.modules.table_description.services import TableDescriptionService
    from app.modules.sql_generation.models import LLMConfig
    from app.utils.sql_database.scanner import SqlAlchemyScanner

    if not ensure_typesense_or_prompt():
        return

    settings = Settings()
    storage = Storage(settings)
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)
    scanner = SqlAlchemyScanner()

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    console.print(f"[bold]Scanning all tables for '{db_connection.alias}'[/bold]")
    console.print(f"[dim]Schemas: {', '.join(db_connection.schemas)}[/dim]")

    # Step 1: Refresh table list
    if refresh:
        console.print(f"\n[cyan]Step 1:[/cyan] Refreshing table list from database...")
        try:
            with console.status("[bold cyan]Syncing with database...[/bold cyan]"):
                table_service = TableDescriptionService(storage)
                refreshed_tables = table_service.refresh_table_description(db_connection_id)

            new_tables = [t for t in refreshed_tables if t.sync_status == "NOT_SCANNED"]
            console.print(f"  [green]✔[/green] Found {len(refreshed_tables)} tables ({len(new_tables)} new)")

        except Exception as e:
            console.print(f"  [red]✖ Refresh failed:[/red] {str(e)}")
            return
    else:
        console.print(f"\n[cyan]Step 1:[/cyan] Skipping refresh (--no-refresh)")

    # Step 2: Get all tables to scan
    tables_to_scan = table_repo.find_by({"db_connection_id": db_connection_id})

    if not tables_to_scan:
        console.print("[yellow]No tables found to scan[/yellow]")
        return

    console.print(f"\n[cyan]Step 2:[/cyan] Scanning {len(tables_to_scan)} tables...")
    if with_descriptions:
        console.print(f"  [dim]AI descriptions enabled ({model_family}/{model_name})[/dim]")

    # Configure LLM if descriptions requested
    llm_config = None
    if with_descriptions:
        llm_config = LLMConfig(
            model_family=model_family,
            model_name=model_name,
        )

    # Group by schema and scan
    db_connection_service = DatabaseConnectionService(scanner, storage)

    try:
        schemas_processed = set()
        total_scanned = 0

        for table in tables_to_scan:
            schema = table.db_schema
            if schema in schemas_processed:
                continue
            schemas_processed.add(schema)

            schema_tables = [t for t in tables_to_scan if t.db_schema == schema]
            console.print(f"\n  [bold]{schema}[/bold] ({len(schema_tables)} tables)")

            with console.status(f"[bold cyan]Scanning {schema}...[/bold cyan]"):
                database = db_connection_service.get_sql_database(db_connection, schema)
                scanner.scan(
                    database.engine,
                    schema_tables,
                    table_repo,
                    llm_config,
                    instruction or ""
                )

            for t in schema_tables:
                console.print(f"    [green]✔[/green] {t.table_name}")
                total_scanned += 1

        console.print(f"\n[green]✔ Scan complete![/green]")
        console.print(f"  Total tables scanned: {total_scanned}")
        if with_descriptions:
            console.print(f"  AI descriptions: generated")

        # Step 3: Generate MDL semantic layer (if requested)
        if generate_mdl:
            console.print(f"\n[cyan]Step 3:[/cyan] Generating MDL semantic layer...")
            try:
                from app.modules.mdl.repositories import MDLRepository
                from app.modules.mdl.services import MDLService

                mdl_repo = MDLRepository(storage=storage)
                mdl_service = MDLService(
                    repository=mdl_repo,
                    table_description_repo=storage,
                )

                # Generate manifest name if not provided
                manifest_name = mdl_name or f"{db_connection.alias} Semantic Layer"

                # Build MDL from the scanned tables
                with console.status("[bold cyan]Building MDL manifest...[/bold cyan]"):
                    manifest_id = _run_async(
                        mdl_service.build_from_database(
                            db_connection_id=db_connection_id,
                            name=manifest_name,
                            catalog=db_connection.alias,
                            schema=db_connection.schemas[0] if db_connection.schemas else "public",
                            data_source=db_connection.dialect,
                            infer_relationships=True,
                        )
                    )

                # Get the created manifest for summary
                manifest = _run_async(
                    mdl_service.get_manifest(manifest_id)
                )

                console.print(f"  [green]✔[/green] MDL manifest created: {manifest_id}")
                console.print(f"    Name: {manifest_name}")
                console.print(f"    Models: {len(manifest.models) if manifest else 0}")
                console.print(f"    Relationships: {len(manifest.relationships) if manifest else 0}")

            except Exception as e:
                console.print(f"  [red]✖ MDL generation failed:[/red] {str(e)}")

    except Exception as e:
        console.print(f"\n[red]✖ Scanning failed:[/red] {str(e)}")


# ============================================================================
# Database Context
# ============================================================================

@table.command("context")
@click.argument("db_connection_id")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json", "markdown"]), default="text", help="Output format")
@click.option("--include-samples", "-s", is_flag=True, help="Include sample data rows")
@click.option("--include-ddl", "-d", is_flag=True, help="Include DDL/CREATE statements")
@click.option("--output", "-o", type=click.Path(), help="Save context to file")
def db_context(db_connection_id: str, output_format: str, include_samples: bool, include_ddl: bool, output: str):
    """Load and display database context (schema, tables, metadata).

    This command loads all database metadata to help understand the schema
    before running queries or analysis. Essential for AI context.

    Examples:

        # Display context in terminal
        kai table context abc123

        # Include sample data
        kai table context abc123 --include-samples

        # Include DDL statements
        kai table context abc123 --include-ddl

        # Export as markdown
        kai table context abc123 -f markdown -o context.md

        # Export as JSON
        kai table context abc123 -f json -o context.json

        # Full context with everything
        kai table context abc123 -s -d -f markdown -o full_context.md
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.utils.core.encrypt import FernetEncrypt

    if not ensure_typesense_or_prompt():
        return

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Get all tables
    tables = table_repo.find_by({"db_connection_id": db_connection_id})

    if not tables:
        console.print("[yellow]No tables found. Run 'kai table scan-all' first.[/yellow]")
        return

    # Parse connection info (safe, without password)
    fernet = FernetEncrypt()
    try:
        decrypted_uri = fernet.decrypt(db_connection.connection_uri)
        parsed = urlparse(decrypted_uri)
        db_name = parsed.path.lstrip('/')
        db_host = parsed.hostname
    except Exception:
        db_name = "unknown"
        db_host = "unknown"

    # Build context based on format
    if output_format == "json":
        context = _build_json_context(db_connection, tables, include_samples, include_ddl, db_name)
        output_text = json.dumps(context, indent=2, default=str)
    elif output_format == "markdown":
        output_text = _build_markdown_context(db_connection, tables, include_samples, include_ddl, db_name, db_host)
    else:
        output_text = _build_text_context(db_connection, tables, include_samples, include_ddl, db_name, db_host)

    # Output
    if output:
        with open(output, "w") as f:
            f.write(output_text)
        console.print(f"[green]✔ Context saved to {output}[/green]")
        console.print(f"  Tables: {len(tables)}")
        console.print(f"  Format: {output_format}")
    else:
        if output_format == "markdown":
            console.print(Text(output_text))
        else:
            console.print(output_text)


def _build_json_context(db_connection, tables, include_samples, include_ddl, db_name):
    """Build JSON context for database."""
    context = {
        "database": {
            "name": db_name,
            "alias": db_connection.alias,
            "dialect": db_connection.dialect,
            "schemas": db_connection.schemas,
            "description": db_connection.description,
        },
        "tables": []
    }

    for table in tables:
        table_info = {
            "name": table.table_name,
            "schema": table.db_schema,
            "description": table.table_description,
            "columns": [
                {
                    "name": col.name,
                    "type": col.data_type,
                    "description": col.description,
                    "is_primary_key": col.is_primary_key,
                    "is_low_cardinality": col.low_cardinality,
                    "categories": col.categories if col.low_cardinality else None,
                    "foreign_key": {
                        "table": col.foreign_key.reference_table,
                        "column": col.foreign_key.field_name
                    } if col.foreign_key else None
                }
                for col in (table.columns or [])
            ]
        }

        if include_samples and table.examples:
            table_info["sample_data"] = table.examples

        if include_ddl and table.table_schema:
            table_info["ddl"] = table.table_schema

        context["tables"].append(table_info)

    return context


def _build_markdown_context(db_connection, tables, include_samples, include_ddl, db_name, db_host):
    """Build Markdown context for database."""
    lines = []
    lines.append(f"# Database Context: {db_connection.alias}")
    lines.append("")
    lines.append(f"**Database:** {db_name}")
    lines.append(f"**Dialect:** {db_connection.dialect}")
    lines.append(f"**Schemas:** {', '.join(db_connection.schemas)}")
    if db_connection.description:
        lines.append(f"\n**Description:** {db_connection.description}")
    lines.append("")
    lines.append(f"## Tables ({len(tables)} total)")
    lines.append("")

    # Group by schema
    schemas = {}
    for table in tables:
        if table.db_schema not in schemas:
            schemas[table.db_schema] = []
        schemas[table.db_schema].append(table)

    for schema_name, schema_tables in schemas.items():
        lines.append(f"### Schema: {schema_name}")
        lines.append("")

        for table in schema_tables:
            lines.append(f"#### {table.table_name}")
            if table.table_description:
                lines.append(f"_{table.table_description}_")
            lines.append("")

            # Columns table
            if table.columns:
                lines.append("| Column | Type | Description | Key | Categories |")
                lines.append("|--------|------|-------------|-----|------------|")
                for col in table.columns:
                    key = ""
                    if col.is_primary_key:
                        key = "PK"
                    elif col.foreign_key:
                        key = f"FK→{col.foreign_key.reference_table}"

                    categories = ""
                    if col.low_cardinality and col.categories:
                        cats = col.categories[:5]
                        categories = ", ".join(str(c) for c in cats)
                        if len(col.categories) > 5:
                            categories += "..."

                    desc = (col.description or "")[:50]
                    lines.append(f"| {col.name} | {col.data_type} | {desc} | {key} | {categories} |")
                lines.append("")

            # Sample data
            if include_samples and table.examples:
                lines.append("**Sample Data:**")
                lines.append("```json")
                lines.append(json.dumps(table.examples[:3], indent=2, default=str))
                lines.append("```")
                lines.append("")

            # DDL
            if include_ddl and table.table_schema:
                lines.append("**DDL:**")
                lines.append("```sql")
                lines.append(table.table_schema)
                lines.append("```")
                lines.append("")

    return "\n".join(lines)


def _build_text_context(db_connection, tables, include_samples, include_ddl, db_name, db_host):
    """Build plain text context for database."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"DATABASE CONTEXT: {db_connection.alias}")
    lines.append("=" * 60)
    lines.append(f"Database: {db_name}")
    lines.append(f"Host: {db_host}")
    lines.append(f"Dialect: {db_connection.dialect}")
    lines.append(f"Schemas: {', '.join(db_connection.schemas)}")
    if db_connection.description:
        lines.append(f"Description: {db_connection.description}")
    lines.append("")
    lines.append(f"TABLES ({len(tables)} total)")
    lines.append("-" * 60)

    # Group by schema
    schemas = {}
    for table in tables:
        if table.db_schema not in schemas:
            schemas[table.db_schema] = []
        schemas[table.db_schema].append(table)

    for schema_name, schema_tables in schemas.items():
        lines.append(f"\n[Schema: {schema_name}]")

        for table in schema_tables:
            lines.append(f"\n  TABLE: {table.table_name}")
            if table.table_description:
                lines.append(f"  Description: {table.table_description}")

            if table.columns:
                lines.append("  Columns:")
                for col in table.columns:
                    key_info = ""
                    if col.is_primary_key:
                        key_info = " [PK]"
                    elif col.foreign_key:
                        key_info = f" [FK→{col.foreign_key.reference_table}]"

                    cat_info = ""
                    if col.low_cardinality and col.categories:
                        cats = ", ".join(str(c) for c in col.categories[:5])
                        if len(col.categories) > 5:
                            cats += "..."
                        cat_info = f" (values: {cats})"

                    desc = f" - {col.description}" if col.description else ""
                    lines.append(f"    - {col.name} ({col.data_type}){key_info}{desc}{cat_info}")

            if include_samples and table.examples:
                lines.append("  Sample Data:")
                for i, row in enumerate(table.examples[:3]):
                    lines.append(f"    Row {i+1}: {row}")

            if include_ddl and table.table_schema:
                lines.append("  DDL:")
                for ddl_line in table.table_schema.split("\n"):
                    lines.append(f"    {ddl_line}")

    return "\n".join(lines)


# ============================================================================
# Search Tables
# ============================================================================

@table.command("search")
@click.argument("db_connection_id")
@click.argument("pattern")
@click.option("--search-in", "-i", type=click.Choice(["all", "tables", "columns", "descriptions"]), default="all", help="Where to search")
@click.option("--case-sensitive", "-c", is_flag=True, help="Case-sensitive search")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def search_tables(db_connection_id: str, pattern: str, search_in: str, case_sensitive: bool, output_format: str):
    """Search tables and columns using wildcard patterns.

    Supports glob-style wildcards:
    - '*' matches any characters (e.g., '*kpi*' matches 'sales_kpi', 'kpi_metrics')
    - '?' matches single character (e.g., 'user?' matches 'users', 'user1')
    - Plain text does contains search (e.g., 'revenue' finds anything containing 'revenue')

    Examples:

        # Search for anything containing 'kpi'
        kai table search abc123 "kpi"

        # Search for columns ending with '_id'
        kai table search abc123 "*_id"

        # Search for tables starting with 'dim_'
        kai table search abc123 "dim_*" --search-in tables

        # Search only in descriptions
        kai table search abc123 "revenue" -i descriptions

        # Case-sensitive search
        kai table search abc123 "KPI" --case-sensitive

        # Output as JSON
        kai table search abc123 "*order*" -f json
    """
    import fnmatch
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository

    if not ensure_typesense_or_prompt():
        return

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Get tables
    tables = table_repo.find_by({"db_connection_id": db_connection_id})
    if not tables:
        console.print("[yellow]No tables found. Run 'kai table scan-all' first.[/yellow]")
        return

    # Convert pattern to regex
    if '*' not in pattern and '?' not in pattern:
        regex_pattern = f".*{re.escape(pattern)}.*"
    else:
        regex_pattern = fnmatch.translate(pattern)
        regex_pattern = regex_pattern.replace(r'\Z', '')

    flags = 0 if case_sensitive else re.IGNORECASE
    compiled_pattern = re.compile(regex_pattern, flags)

    # Search results
    results = {
        "tables": [],
        "columns": [],
        "descriptions": []
    }

    for table in tables:
        table_full_name = f"{table.db_schema}.{table.table_name}"

        # Search in table names
        if search_in in ("all", "tables"):
            if compiled_pattern.search(table.table_name):
                results["tables"].append({
                    "table": table_full_name,
                    "description": table.table_description,
                    "columns": len(table.columns) if table.columns else 0
                })

        # Search in table descriptions
        if search_in in ("all", "descriptions"):
            if table.table_description and compiled_pattern.search(table.table_description):
                already_matched = any(m["table"] == table_full_name for m in results["tables"])
                if not already_matched:
                    results["descriptions"].append({
                        "type": "table",
                        "table": table_full_name,
                        "description": table.table_description[:100] + "..." if len(table.table_description or "") > 100 else table.table_description
                    })

        # Search in columns
        if table.columns:
            for col in table.columns:
                if search_in in ("all", "columns"):
                    if compiled_pattern.search(col.name):
                        results["columns"].append({
                            "table": table_full_name,
                            "column": col.name,
                            "type": col.data_type,
                            "description": col.description
                        })

                if search_in in ("all", "descriptions"):
                    if col.description and compiled_pattern.search(col.description):
                        already_matched = any(
                            m.get("column") == col.name and m.get("table") == table_full_name
                            for m in results["columns"]
                        )
                        if not already_matched:
                            results["descriptions"].append({
                                "type": "column",
                                "table": table_full_name,
                                "column": col.name,
                                "description": col.description[:100] + "..." if len(col.description or "") > 100 else col.description
                            })

    total = len(results["tables"]) + len(results["columns"]) + len(results["descriptions"])

    if output_format == "json":
        console.print(json.dumps(results, indent=2, default=str))
        return

    # Text output
    console.print(f"[bold]Search results for pattern '{pattern}'[/bold]")
    console.print(f"[dim]Searching in: {search_in} | Case-sensitive: {case_sensitive}[/dim]\n")

    if total == 0:
        console.print("[yellow]No matches found[/yellow]")
        console.print("[dim]Tips: Try a broader pattern like '*kpi*' or search in 'all'[/dim]")
        return

    if results["tables"]:
        console.print(f"[cyan]Tables ({len(results['tables'])}):[/cyan]")
        for m in results["tables"]:
            console.print(f"  [green]●[/green] [bold]{m['table']}[/bold] ({m['columns']} columns)")
            if m["description"]:
                desc = m["description"][:80] + "..." if len(m["description"] or "") > 80 else m["description"]
                console.print(f"      [dim]{desc}[/dim]")
        console.print()

    if results["columns"]:
        console.print(f"[cyan]Columns ({len(results['columns'])}):[/cyan]")
        for m in results["columns"]:
            console.print(f"  [green]●[/green] [bold]{m['table']}[/bold].[cyan]{m['column']}[/cyan] ({m['type']})")
            if m["description"]:
                desc = m["description"][:80] + "..." if len(m["description"] or "") > 80 else m["description"]
                console.print(f"      [dim]{desc}[/dim]")
        console.print()

    if results["descriptions"]:
        console.print(f"[cyan]Description matches ({len(results['descriptions'])}):[/cyan]")
        for m in results["descriptions"]:
            if m["type"] == "table":
                console.print(f"  [yellow]●[/yellow] Table: [bold]{m['table']}[/bold]")
            else:
                console.print(f"  [yellow]●[/yellow] Column: [bold]{m['table']}[/bold].[cyan]{m['column']}[/cyan]")
            console.print(f"      [dim]{m['description']}[/dim]")
        console.print()

    console.print(f"[green]Total matches: {total}[/green]")
