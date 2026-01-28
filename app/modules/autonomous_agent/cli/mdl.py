"""MDL (Model Definition Language) commands for KAI Autonomous Agent.

This module provides commands for managing MDL manifests:
- List and search MDL manifests
- Show detailed manifest information
- Export manifests to JSON or Markdown
"""
import json

import click
from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD

from app.modules.autonomous_agent.cli import (
    console,
    ensure_typesense_or_prompt,
    _run_async,
)

# ============================================================================
# MDL Command Group
# ============================================================================

@click.group()
def mdl():
    """MDL (semantic layer) management commands.

    The MDL provides semantic context that improves KAI's reasoning about
    your data, including relationships, calculated fields, and business
    terminology.

    Examples:

        kai-agent mdl list                    # List all manifests

        kai-agent mdl show koperasi           # Show manifest for database
    """
    pass


# ============================================================================
# List MDL Manifests
# ============================================================================

@mdl.command("list")
@click.option("--db", "db_identifier", help="Filter by database connection ID or alias")
def list_manifests(db_identifier: str | None):
    """List MDL manifests.

    Examples:

        kai-agent mdl list                    # List all manifests

        kai-agent mdl list --db koperasi      # List manifests for a database
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository
    from app.modules.mdl.services import MDLService
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    if not ensure_typesense_or_prompt(required=True):
        return

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)
    mdl_service = MDLService(repository=mdl_repo)
    db_repo = DatabaseConnectionRepository(storage)

    # Resolve db_identifier to connection_id if provided
    db_connection_id = None
    if db_identifier:
        from app.modules.autonomous_agent.cli import resolve_db_identifier
        db_conn = resolve_db_identifier(db_identifier, db_repo)
        if not db_conn:
            console.print(f"[red]Database connection '{db_identifier}' not found[/red]")
            console.print("[dim]Tip: Use 'kai-agent connection list' to see available databases[/dim]")
            return
        db_connection_id = db_conn.id

    # Fetch manifests
    manifests = _run_async(
        mdl_service.list_manifests(db_connection_id=db_connection_id)
    )

    if not manifests:
        if db_connection_id:
            console.print(f"[yellow]No MDL manifests found for database '{db_identifier}'[/yellow]")
            console.print("[dim]Tip: Use 'kai-agent connection scan-all --generate-mdl' to create one[/dim]")
        else:
            console.print("[yellow]No MDL manifests found[/yellow]")
            console.print("[dim]Tip: Use 'kai-agent connection scan-all <db> --generate-mdl' to create one[/dim]")
        return

    # Display table
    table = Table(
        title="MDL Manifests",
        box=MINIMAL_DOUBLE_HEAD,
        show_header=True,
        show_lines=True,
        row_styles=["dim", ""],  # Zebra striping
        expand=True
    )
    table.add_column("ID", style="cyan", no_wrap=False)
    table.add_column("Name", style="green")
    table.add_column("Database", style="blue")
    table.add_column("Catalog")
    table.add_column("Schema")
    table.add_column("Models", justify="right")
    table.add_column("Relationships", justify="right")
    table.add_column("Created")

    for manifest in manifests:
        # Get database connection for alias
        db_conn = db_repo.find_by_id(manifest.db_connection_id)
        db_name = db_conn.alias if db_conn else manifest.db_connection_id[:8]

        # Format created_at (handle both string and datetime)
        created_str = "-"
        if manifest.created_at:
            if isinstance(manifest.created_at, str):
                created_str = manifest.created_at[:10]
            else:
                created_str = manifest.created_at.strftime("%Y-%m-%d")

        table.add_row(
            manifest.id[:8] + "...",
            manifest.name,
            db_name,
            manifest.catalog or "-",
            manifest.schema_name or "-",
            str(len(manifest.models) if manifest.models else 0),
            str(len(manifest.relationships) if manifest.relationships else 0),
            created_str
        )

    console.print(table)


# ============================================================================
# Show MDL Manifest
# ============================================================================

@mdl.command("show")
@click.argument("manifest_identifier")
@click.option("--summary", is_flag=True, help="Show summary only (hide details)")
@click.option(
    "--format", "-f",
    type=click.Choice(["terminal", "json", "markdown"]),
    default="terminal",
    help="Output format"
)
@click.option("--output", "-o", type=click.Path(), help="Save to file")
def show_manifest(manifest_identifier: str, summary: bool, format: str, output: str | None):
    """Show MDL manifest details.

    MANIFEST_IDENTIFIER: Manifest ID, database alias, or database connection ID

    Examples:

        kai-agent mdl show 4f8d0993...           # Show by manifest ID

        kai-agent mdl show koperasi              # Show latest MDL for database alias

        kai-agent mdl show 4f8d0993 --summary    # Show summary only

        kai-agent mdl show koperasi -f json      # Export as JSON

        kai-agent mdl show koperasi -f markdown -o mdl.md  # Export as Markdown
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository
    from app.modules.mdl.services import MDLService
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    if not ensure_typesense_or_prompt(required=True):
        return

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)
    mdl_service = MDLService(repository=mdl_repo)
    db_repo = DatabaseConnectionRepository(storage)

    # Resolve identifier
    resolved = _resolve_manifest_identifier(manifest_identifier, mdl_service, db_repo)
    if not resolved:
        console.print(f"[red]MDL manifest '{manifest_identifier}' not found[/red]")
        console.print("[dim]Tip: Use 'kai-agent mdl list' to see available manifests[/dim]")
        return

    manifest_id, db_conn = resolved

    # Fetch manifest
    manifest = _run_async(mdl_service.get_manifest(manifest_id))
    if not manifest:
        console.print(f"[red]Failed to load manifest: {manifest_id}[/red]")
        return

    # Handle different output formats
    if format == "json":
        output_data = manifest.to_dict()
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            console.print(f"[green]✔ Exported to:[/green] {output}")
        else:
            console.print(json.dumps(output_data, indent=2, default=str))
        return

    if format == "markdown":
        md_content = _manifest_to_markdown(manifest, db_conn)
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(md_content)
            console.print(f"[green]✔ Exported to:[/green] {output}")
        else:
            console.print(md_content)
        return

    # Terminal format (default)
    _display_manifest_terminal(manifest, db_conn, summary)


# ============================================================================
# Helper Functions
# ============================================================================

def _resolve_manifest_identifier(
    identifier: str,
    mdl_service,
    db_repo
) -> tuple[str, object] | None:
    """Resolve manifest identifier to manifest ID and database connection.

    Tries multiple strategies:
    1. As manifest ID (UUID)
    2. As database alias
    3. As database connection ID

    Args:
        identifier: Manifest ID, database alias, or database connection ID
        mdl_service: MDLService instance
        db_repo: DatabaseConnectionRepository instance

    Returns:
        Tuple of (manifest_id, database_connection) or None if not found
    """
    from app.modules.mdl.models import MDLManifest

    # Try as manifest ID first (UUID)
    if len(identifier.replace("-", "")) == 32:
        try:
            manifest = _run_async(mdl_service.get_manifest(identifier))
            if manifest:
                db_conn = db_repo.find_by_id(manifest.db_connection_id)
                if db_conn:
                    return identifier, db_conn
        except Exception:
            pass

    # Try as database alias
    from app.modules.autonomous_agent.cli import resolve_db_identifier
    db_conn = resolve_db_identifier(identifier, db_repo)
    if db_conn:
        manifest = _run_async(
            mdl_service.get_manifest_by_db_connection(db_conn.id)
        )
        if manifest:
            return manifest.id, db_conn

    return None


def _display_manifest_terminal(manifest, db_conn, summary: bool):
    """Display manifest in Rich terminal format."""
    # Summary panel
    summary_lines = [
        f"[cyan]ID:[/cyan] {manifest.id}",
        f"[cyan]Database:[/cyan] {db_conn.alias if db_conn else manifest.db_connection_id[:8]}",
        f"[cyan]Catalog:[/cyan] {manifest.catalog or '-'}",
        f"[cyan]Schema:[/cyan] {manifest.schema_name or '-'}",
        f"[cyan]Data Source:[/cyan] {manifest.data_source or '-'}",
        "",
        f"[cyan]Models:[/cyan] {len(manifest.models) if manifest.models else 0}",
        f"[cyan]Relationships:[/cyan] {len(manifest.relationships) if manifest.relationships else 0}",
        f"[cyan]Metrics:[/cyan] {len(manifest.metrics) if manifest.metrics else 0}",
        f"[cyan]Views:[/cyan] {len(manifest.views) if manifest.views else 0}",
    ]

    if manifest.created_at:
        created_str = manifest.created_at if isinstance(manifest.created_at, str) else manifest.created_at.strftime('%Y-%m-%d %H:%M')
        summary_lines.append("")
        summary_lines.append(f"[cyan]Created:[/cyan] {created_str}")

    console.print(Panel(
        "\n".join(summary_lines),
        title=f"[bold green]{manifest.name}[/bold green]",
        border_style="cyan"
    ))

    if summary:
        return

    # Show models
    if manifest.models:
        console.print("\n[bold cyan]Models:[/bold cyan]")
        for model in manifest.models[:20]:  # Limit to first 20
            model_info = f"  [green]{model.name}[/green]"
            if model.ref_sql:
                model_info += f" [dim](refSql)[/dim]"
            console.print(model_info)

            if model.columns:
                col_table = Table(show_header=True, box=MINIMAL_DOUBLE_HEAD, expand=True)
                col_table.add_column("Column", style="cyan")
                col_table.add_column("Type")
                col_table.add_column("PK")
                col_table.add_column("Calc")
                col_table.add_column("Relationship")

                for col in model.columns[:10]:  # Limit columns
                    # Check if this column is the primary key
                    is_pk = col.name == model.primary_key if model.primary_key else False

                    col_table.add_row(
                        col.name,
                        col.type or "-",
                        "✓" if is_pk else "",
                        "✓" if col.is_calculated else "",
                        col.relationship or ""
                    )
                console.print(col_table)

        if len(manifest.models) > 20:
            console.print(f"[dim]  ... and {len(manifest.models) - 20} more models[/dim]")

    # Show relationships
    if manifest.relationships:
        console.print("\n[bold cyan]Relationships:[/bold cyan]")
        for rel in manifest.relationships[:20]:
            rel_info = (
                f"  [blue]{rel.name}[/blue] "
                f"({rel.cardinality or 'UNKNOWN'})\n"
                f"    [dim]{rel.model1}.{rel.field1} = {rel.model2}.{rel.field2}[/dim]"
            )
            console.print(rel_info)

        if len(manifest.relationships) > 20:
            console.print(f"[dim]  ... and {len(manifest.relationships) - 20} more relationships[/dim]")

    # Show metrics
    if manifest.metrics:
        console.print("\n[bold cyan]Metrics:[/bold cyan]")
        for metric in manifest.metrics[:10]:
            console.print(f"  [magenta]{metric.name}[/magenta]: {metric.expression or metric.base_model or '-'}")


def _manifest_to_markdown(manifest, db_conn) -> str:
    """Convert manifest to Markdown format."""
    lines = [
        f"# {manifest.name}",
        "",
        "## Metadata",
        "",
        f"- **ID**: `{manifest.id}`",
        f"- **Database**: {db_conn.alias if db_conn else manifest.db_connection_id[:8]}",
        f"- **Catalog**: {manifest.catalog or '-'}",
        f"- **Schema**: {manifest.schema_name or '-'}",
        f"- **Data Source**: {manifest.data_source or '-'}",
        f"- **Created**: {manifest.created_at if isinstance(manifest.created_at, str) else (manifest.created_at.strftime('%Y-%m-%d %H:%M:%S') if manifest.created_at else '-')}",
        "",
        f"## Summary",
        "",
        f"- **Models**: {len(manifest.models) if manifest.models else 0}",
        f"- **Relationships**: {len(manifest.relationships) if manifest.relationships else 0}",
        f"- **Metrics**: {len(manifest.metrics) if manifest.metrics else 0}",
        f"- **Views**: {len(manifest.views) if manifest.views else 0}",
        "",
    ]

    # Models
    if manifest.models:
        lines.extend([
            "## Models",
            "",
        ])
        for model in manifest.models:
            lines.append(f"### {model.name}")
            lines.append("")
            if model.ref_sql:
                lines.append(f"**Reference SQL:** `{model.ref_sql[:100]}...`")
                lines.append("")

            if model.columns:
                lines.append("| Column | Type | Primary Key | Calculated | Relationship |")
                lines.append("|--------|------|-------------|------------|--------------|")
                for col in model.columns[:50]:
                    # Check if this column is the primary key
                    is_pk = col.name == model.primary_key if model.primary_key else False

                    lines.append(
                        f"| {col.name} | {col.type or '-'} | "
                        f"{'✓' if is_pk else ''} | "
                        f"{'✓' if col.is_calculated else ''} | "
                        f"{col.relationship or '-'} |"
                    )
                lines.append("")

    # Relationships
    if manifest.relationships:
        lines.extend([
            "## Relationships",
            "",
        ])
        for rel in manifest.relationships:
            lines.extend([
                f"### {rel.name}",
                "",
                f"- **Type**: {rel.cardinality or 'UNKNOWN'}",
                f"- **Join**: `{rel.model1}.{rel.field1} = {rel.model2}.{rel.field2}`",
                "",
            ])

    # Metrics
    if manifest.metrics:
        lines.extend([
            "## Metrics",
            "",
        ])
        for metric in manifest.metrics:
            lines.extend([
                f"### {metric.name}",
                "",
                f"**Expression**: `{metric.expression or metric.base_model or '-'}`",
                "",
            ])

    return "\n".join(lines)
