"""Context CLI commands for KAI.

This command group provides functionality for managing context assets
including table descriptions, glossaries, instructions, and skills.
"""

import json
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from app.modules.autonomous_agent.cli import console, ensure_typesense_or_prompt, _run_async
from app.modules.autonomous_agent.modules import _resolve_db_identifier


@click.group()
def context():
    """Context asset commands.

    Manage context assets for improving autonomous agent performance.
    Create, list, view, update, and promote assets across lifecycle states.
    """
    pass


# ============================================================================
# List Context Assets
# ============================================================================

@context.command("list")
@click.option("--db", "-d", required=True, help="Database connection ID or alias")
@click.option("--type", "asset_type", type=click.Choice(["table_description", "glossary", "instruction", "skill"]), help="Filter by asset type")
@click.option("--state", "lifecycle_state", type=click.Choice(["draft", "verified", "published", "deprecated"]), help="Filter by lifecycle state")
@click.option("--limit", type=int, default=50, help="Maximum number of assets to return")
def list_context_assets(db, asset_type, lifecycle_state, limit):
    """List context assets.

    Examples:

        kai context list --db mydb

        kai context list --db mydb --type instruction --state published
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)
    db_repo = get_db_connection_repository(storage)

    # Resolve database identifier
    db_conn = _resolve_db_identifier(db, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db}' not found[/red]")
        return

    # Convert string to enum
    from app.modules.context_platform.models.asset import ContextAssetType, LifecycleState

    asset_type_enum = ContextAssetType(asset_type) if asset_type else None
    state_enum = LifecycleState(lifecycle_state) if lifecycle_state else None

    assets = service.list_assets(
        db_connection_id=db_conn["id"],
        asset_type=asset_type_enum,
        lifecycle_state=state_enum,
        limit=limit
    )

    if not assets:
        console.print("[yellow]No context assets found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Key", style="white")
    table.add_column("Name", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Version", style="blue")
    table.add_column("Updated", style="dim")

    for asset in assets[:limit]:  # Limit to requested number
        asset_type = str(asset.asset_type.value if hasattr(asset.asset_type, 'value') else asset.asset_type)
        canonical_key = asset.canonical_key or "unknown"
        name = asset.name or "Unknown"
        state = str(asset.lifecycle_state.value if hasattr(asset.lifecycle_state, 'value') else asset.lifecycle_state)
        version = asset.version or "1.0.0"
        updated_at: str = asset.updated_at or "Unknown"

        # Format timestamp
        if updated_at and updated_at != "Unknown":
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(updated_at)
                updated_at = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        table.add_row(asset_type, canonical_key[:30], name[:40], state, version, str(updated_at))

    console.print(f"\n[bold]Context Assets for:[/bold] {db_conn.get('alias', db)}\n")
    console.print(table)

    if asset_type:
        console.print(f"[dim]Filtered by type: {asset_type}[/dim]")
    if lifecycle_state:
        console.print(f"[dim]Filtered by state: {lifecycle_state}[/dim]")
    console.print(f"[dim]Showing {min(len(assets), limit)} asset(s)[/dim]")


# ============================================================================
# Show Context Asset
# ============================================================================

@context.command("show")
@click.argument("asset_id")
def show_context_asset(asset_id):
    """Show details of a context asset.

    Examples:

        kai context show asset_123
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)

    # Get asset
    from app.modules.context_platform.models.asset import LifecycleState

    asset = None
    # Try to get by ID
    try:
        # The service doesn't have a get_by_id method, so we need to search
        # For now, we'll use a direct storage query
        result = storage.find_by_id("context_assets", asset_id)
        if result:
            asset = result
    except:
        pass

    if not asset:
        console.print(f"[red]✖ Asset '{asset_id}' not found[/red]")
        return

    # Display asset details
    console.print(f"\n[bold]Context Asset:[/bold] {asset.get('name', 'Unknown')}")
    console.print(f"ID: {asset.get('id')}")
    console.print(f"Type: {asset.get('asset_type', 'unknown')}")
    console.print(f"Key: {asset.get('canonical_key', 'unknown')}")
    console.print(f"Database: {asset.get('db_connection_id', 'unknown')}")
    console.print(f"Lifecycle: {asset.get('lifecycle_state', 'unknown')}")
    console.print(f"Version: {asset.get('version', '1.0.0')}")

    # Content
    content = asset.get("content", {})
    if content:
        console.print(f"\n[bold]Content:[/bold]")
        if isinstance(content, dict):
            # Pretty print JSON
            content_str = json.dumps(content, indent=2)
            console.print(Panel(Syntax(content_str, "json", theme="monokai"), title="Content"))
        else:
            console.print(Panel(str(content), title="Content"))

    # Tags
    tags = asset.get("tags", [])
    if tags:
        console.print(f"\n[bold]Tags:[/bold] {', '.join(tags)}")

    # Metadata
    author = asset.get("author")
    if author:
        console.print(f"Author: {author}")

    created_at = asset.get("created_at")
    updated_at = asset.get("updated_at")
    if created_at or updated_at:
        console.print(f"\n[dim]Created: {created_at}[/dim]")
        console.print(f"[dim]Updated: {updated_at}[/dim]")


# ============================================================================
# Promote Context Asset
# ============================================================================

@context.command("promote")
@click.argument("asset_id")
@click.argument("target_state", type=click.Choice(["verified", "published"]))
@click.option("--by", "promoted_by", required=True, help="Who is promoting this asset")
@click.option("--note", "change_note", help="Reason for promotion")
def promote_context_asset(asset_id, target_state, promoted_by, change_note):
    """Promote a context asset to the next lifecycle state.

    Promotes an asset through the lifecycle: draft -> verified -> published

    Examples:

        kai context promote asset_123 verified --by "Jane Doe"

        kai context promote asset_123 published --by "Jane Doe" --note "Approved for production"
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService, LifecyclePolicyError

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)

    try:
        if target_state == "verified":
            asset = service.promote_to_verified(asset_id, promoted_by, change_note)
            console.print(f"[green]✔ Asset promoted to verified[/green]")
        elif target_state == "published":
            asset = service.promote_to_published(asset_id, promoted_by, change_note)
            console.print(f"[green]✔ Asset promoted to published[/green]")

        if asset:
            console.print(f"Asset: {asset.name or asset_id}")
            console.print(f"New state: {target_state}")

    except LifecyclePolicyError as e:
        console.print(f"[red]✖ Promotion failed:[/red] {e}")
    except Exception as e:
        console.print(f"[red]✖ Error:[/red] {e}")


# ============================================================================
# Deprecate Context Asset
# ============================================================================

@context.command("deprecate")
@click.argument("asset_id")
@click.option("--by", "promoted_by", required=True, help="Who is deprecating this asset")
@click.option("--reason", "reason", required=True, help="Reason for deprecation")
def deprecate_context_asset(asset_id, promoted_by, reason):
    """Deprecate a context asset.

    Marks an asset as deprecated. Can be called from any state.

    Examples:

        kai context deprecate asset_123 --by "Jane Doe" --reason "Replaced by new version"
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)

    try:
        asset = service.deprecate_asset(asset_id, promoted_by, reason)

        if asset:
            console.print(f"[green]✔ Asset deprecated[/green]")
            console.print(f"Asset: {asset.name or asset_id}")
            console.print(f"New state: deprecated")

    except Exception as e:
        console.print(f"[red]✖ Error:[/red] {e}")


# ============================================================================
# Create Context Asset
# ============================================================================

@context.command("create")
@click.option("--db", "-d", required=True, help="Database connection ID or alias")
@click.option("--type", "asset_type", type=click.Choice(["table_description", "glossary", "instruction", "skill"]), required=True, help="Asset type")
@click.option("--key", "canonical_key", required=True, help="Unique key for this asset")
@click.option("--name", required=True, help="Asset name")
@click.option("--description", help="Asset description")
@click.option("--content-file", type=click.Path(exists=True), help="JSON file with asset content")
@click.option("--content", help="Asset content as JSON string")
@click.option("--tags", help="Comma-separated tags")
@click.option("--author", help="Asset creator")
def create_context_asset(db, asset_type, canonical_key, name, description, content_file, content, tags, author):
    """Create a new context asset.

    The asset content can be provided via --content-file or --content.

    Examples:

        kai context create --db mydb --type instruction --key sales_analysis --name "Sales Analysis" --content '{"prompt": "..."}'

        kai context create --db mydb --type glossary --key terms --name "Business Terms" --content-file glossary.json
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)
    db_repo = get_db_connection_repository(storage)

    # Resolve database identifier
    db_conn = _resolve_db_identifier(db, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db}' not found[/red]")
        return

    # Parse content
    asset_content = None
    content_text = ""

    if content_file:
        with open(content_file, 'r') as f:
            asset_content = json.load(f)
        content_text = json.dumps(asset_content)
    elif content:
        asset_content = json.loads(content)
        content_text = content
    else:
        console.print("[red]✖ Either --content-file or --content is required[/red]")
        return

    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]

    # Convert to enum
    from app.modules.context_platform.models.asset import ContextAssetType

    try:
        asset_type_enum = ContextAssetType(asset_type)

        asset = service.create_asset(
            db_connection_id=db_conn["id"],
            asset_type=asset_type_enum,
            canonical_key=canonical_key,
            name=name,
            description=description,
            content=asset_content,
            content_text=content_text,
            author=author,
            tags=tag_list,
        )

        console.print(f"\n[green]✔ Context asset created[/green]")
        console.print(f"ID: {asset.id}")
        console.print(f"Name: {asset.name}")
        console.print(f"Type: {asset.asset_type.value}")
        console.print(f"Key: {asset.canonical_key}")
        console.print(f"State: {asset.lifecycle_state.value}")

    except Exception as e:
        console.print(f"[red]✖ Error creating asset:[/red] {e}")


# ============================================================================
# Update Context Asset
# ============================================================================

@context.command("update")
@click.argument("asset_id")
@click.option("--name", help="New asset name")
@click.option("--description", help="New description")
@click.option("--content-file", type=click.Path(exists=True), help="JSON file with updated content")
@click.option("--content", help="Updated content as JSON string")
@click.option("--tags", help="Comma-separated tags (replaces existing)")
def update_context_asset(asset_id, name, description, content_file, content, tags):
    """Update a context asset.

    Examples:

        kai context update asset_123 --name "New Name"

        kai context update asset_123 --content-file updated.json
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)

    # Parse content
    asset_content = None
    content_text = None

    if content_file:
        with open(content_file, 'r') as f:
            asset_content = json.load(f)
        content_text = json.dumps(asset_content)
    elif content:
        asset_content = json.loads(content)
        content_text = content

    # Parse tags
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]

    try:
        asset = service.update_asset(
            asset_id=asset_id,
            name=name,
            description=description,
            content=asset_content,
            content_text=content_text,
            tags=tag_list,
        )

        if asset:
            console.print(f"[green]✔ Context asset updated[/green]")
            console.print(f"ID: {asset_id}")
            console.print(f"Name: {asset.name}")
        else:
            console.print(f"[yellow]⚠ Asset not found: {asset_id}[/yellow]")

    except Exception as e:
        console.print(f"[red]✖ Error updating asset:[/red] {e}")


# ============================================================================
# Delete Context Asset
# ============================================================================

@context.command("delete")
@click.argument("db_connection_id")
@click.argument("asset_type")
@click.argument("canonical_key")
@click.option("--version", "-v", default="latest", help="Version to delete (default: latest)")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete_context_asset(db_connection_id, asset_type, canonical_key, version, force):
    """Delete a context asset.

    Examples:

        kai context delete mydb instruction sales_analysis

        kai context delete mydb instruction sales_analysis --version 1.0.0
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)
    db_repo = get_db_connection_repository(storage)

    # Resolve database identifier
    db_conn = _resolve_db_identifier(db_connection_id, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db_connection_id}' not found[/red]")
        return

    # Convert to enum
    from app.modules.context_platform.models.asset import ContextAssetType

    try:
        asset_type_enum = ContextAssetType(asset_type)

        if not force:
            if not click.confirm(f"Delete {asset_type}/{canonical_key}@{version}?", default=False):
                console.print("Cancelled")
                return

        deleted = service.delete_asset(
            db_connection_id=db_conn["id"],
            asset_type=asset_type_enum,
            canonical_key=canonical_key,
            version=version,
        )

        if deleted:
            console.print(f"[green]✔ Asset deleted:[/green] {asset_type}/{canonical_key}@{version}")
        else:
            console.print(f"[yellow]⚠ Asset not found: {asset_type}/{canonical_key}@{version}[/yellow]")

    except Exception as e:
        console.print(f"[red]✖ Error deleting asset:[/red] {e}")


# ============================================================================
# Search Context Assets
# ============================================================================

@context.command("search")
@click.option("--db", "-d", required=True, help="Database connection ID or alias")
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--limit", type=int, default=10, help="Maximum results to return")
def search_context_assets(db, query, limit):
    """Search context assets by content.

    Performs semantic and keyword search across asset content.

    Examples:

        kai context search --db mydb --query "sales analysis"

        kai context search --db mydb --query "glossary terms" --limit 20
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)
    db_repo = get_db_connection_repository(storage)

    # Resolve database identifier
    db_conn = _resolve_db_identifier(db, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db}' not found[/red]")
        return

    try:
        # Create a mock search request
        from app.api.requests import SearchContextAssetsRequest

        request = SearchContextAssetsRequest(
            db_connection_id=db_conn["id"],
            query=query,
            limit=limit,
        )

        results = service.search_assets(
            db_connection_id=request.db_connection_id,
            query=request.query,
            asset_type=None,
            limit=request.limit,
        )

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Key", style="white")
        table.add_column("Name", style="green")
        table.add_column("Score", style="yellow")

        for result in results[:limit]:
            asset = result.asset
            score = result.score

            table.add_row(
                str(asset.asset_type.value if hasattr(asset.asset_type, 'value') else asset.asset_type),
                (asset.canonical_key or "unknown")[:30],
                (asset.name or "Unknown")[:40],
                f"{score:.2f}"
            )

        console.print(f"\n[bold]Search Results for:[/bold] '{query}'")
        console.print(table)
        console.print(f"[dim]Showing {min(len(results), limit)} result(s)[/dim]")

    except Exception as e:
        console.print(f"[red]✖ Error searching assets:[/red] {e}")


# ============================================================================
# Tags Commands
# ============================================================================

@context.command("tags")
@click.option("--category", help="Filter tags by category")
def list_tags(category):
    """List all context asset tags.

    Examples:

        kai context tags

        kai context tags --category domain
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.context_platform.services.asset_service import ContextAssetService

    settings = Settings()
    storage = Storage(settings)
    service = ContextAssetService(storage)

    try:
        tags = service.get_tags(category=category)

        if not tags:
            console.print("[yellow]No tags found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tag", style="cyan")
        table.add_column("Category", style="white")
        table.add_column("Usage", style="yellow")

        for tag in tags:
            tag_name = tag.name or "unknown"
            tag_category = tag.category or "none"
            usage_count = tag.usage_count

            table.add_row(tag_name, tag_category, str(usage_count))

        console.print(f"\n[bold]Context Asset Tags[/bold]\n")
        console.print(table)

        if category:
            console.print(f"[dim]Filtered by category: {category}[/dim]")

    except Exception as e:
        console.print(f"[red]✖ Error fetching tags:[/red] {e}")


# ============================================================================
# Sync Context to Filesystem
# ============================================================================

@context.command("sync")
@click.option("--db", "-d", required=True, help="Database connection ID or alias")
@click.option(
    "--output-dir",
    default=None,
    help="Output directory (default: CONTEXT_DIR env var or ./context)",
)
@click.option(
    "--include-preview/--no-preview",
    default=True,
    show_default=True,
    help="Include sample data preview files",
)
@click.option(
    "--preview-rows",
    type=int,
    default=5,
    show_default=True,
    help="Number of sample rows in preview files",
)
def sync_context(db, output_dir, include_preview, preview_rows):
    """Sync context assets to the local filesystem as Markdown files.

    Exports table schemas, glossary terms, and instruction assets
    into a structured directory for offline agent use.

    Examples:

        kai context sync --db mydb

        kai context sync --db mydb --output-dir ./context --no-preview

        kai context sync --db mydb --preview-rows 10
    """
    import os

    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.autonomous_agent.modules import get_db_connection_repository, _resolve_db_identifier
    from app.modules.autonomous_agent.context_sync import ContextSyncService

    if output_dir is None:
        output_dir = os.environ.get("CONTEXT_DIR", "./context")

    settings = Settings()
    storage = Storage(settings)
    db_repo = get_db_connection_repository(storage)

    db_conn = _resolve_db_identifier(db, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db}' not found[/red]")
        console.print("[dim]Use 'kai connection list' to see available connections[/dim]")
        return

    db_connection_id = db_conn["id"] if isinstance(db_conn, dict) else db_conn.id
    db_alias = db_conn.get("alias") if isinstance(db_conn, dict) else db_conn.alias

    service = ContextSyncService(storage)

    console.print(f"\n[cyan]Syncing context for:[/cyan] {db_alias or db_connection_id}")
    console.print(f"[dim]Output directory:[/dim] {output_dir}")
    if include_preview:
        console.print(f"[dim]Preview rows:[/dim] {preview_rows}")

    try:
        with console.status("[bold cyan]Writing context files...[/bold cyan]"):
            result = service.sync(
                db_connection_id=db_connection_id,
                output_dir=output_dir,
                include_preview=include_preview,
                preview_rows=preview_rows,
                db_alias=db_alias,
            )

        summary = Table(show_header=True, header_style="bold magenta")
        summary.add_column("Category", style="cyan")
        summary.add_column("Count", style="white", justify="right")
        summary.add_row("Tables", str(result.table_count))
        summary.add_row("Glossary terms", str(result.glossary_count))
        summary.add_row("Instructions", str(result.instruction_count))
        summary.add_row("Total files written", str(result.file_count))

        console.print(f"\n[green]✔ Context sync complete[/green]")
        console.print(summary)
        console.print(f"[dim]Files written to:[/dim] {output_dir}/")

    except Exception as e:
        console.print(f"[red]✖ Sync failed:[/red] {e}")
