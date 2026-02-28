"""Database connection management commands."""

import json
import click
from rich.panel import Panel

from app.modules.autonomous_agent.cli import console, ensure_typesense_or_prompt


@click.group()
def connection():
    """Database connection management.

    These commands handle creating, listing, updating, and deleting
    database connections for the KAI system.
    """
    pass


@connection.command("create")
@click.argument("connection_uri")
@click.option("--alias", "-a", required=True, help="Human-readable name for the connection")
@click.option("--schema", "-s", "schemas", multiple=True, help="Database schema(s) to use (can be specified multiple times)")
@click.option("--metadata", "-m", type=str, help="JSON metadata for the connection")
def create(connection_uri: str, alias: str, schemas: tuple, metadata: str):
    """Create a new database connection.

    Examples:

        kai connection create "postgresql://user:pass@localhost:5432/mydb" -a my_database

        kai connection create "postgresql://user:pass@host:5432/db" -a prod_db -s public -s analytics

        kai connection create "csv://data.csv" -a sales_data
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import DatabaseConnectionRequest
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.utils.sql_database.scanner import SqlAlchemyScanner

    settings = Settings()
    storage = Storage(settings)
    scanner = SqlAlchemyScanner()
    service = DatabaseConnectionService(scanner, storage)

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    request = DatabaseConnectionRequest(
        alias=alias,
        connection_uri=connection_uri,
        schemas=list(schemas) if schemas else ["public"],
        metadata=meta_dict,
    )

    console.print(f"[bold]Creating connection '{alias}'...[/bold]")
    console.print(f"[dim]URI: {connection_uri[:50]}...[/dim]" if len(connection_uri) > 50 else f"[dim]URI: {connection_uri}[/dim]")
    console.print(f"[dim]Schemas: {', '.join(schemas)}[/dim]")

    try:
        with console.status("[bold cyan]Testing connection and scanning tables...[/bold cyan]"):
            db_connection = service.create_database_connection(request)

        console.print(f"\\n[green]✔ Connection created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {db_connection.id}\\n"
            f"[bold]Alias:[/bold] {db_connection.alias}\\n"
            f"[bold]Dialect:[/bold] {db_connection.dialect}\\n"
            f"[bold]Schemas:[/bold] {', '.join(db_connection.schemas)}",
            title="Connection Details",
            border_style="green"
        ))
        console.print(f"\\n[dim]Use this ID with: kai query run 'your query' --db {db_connection.id}[/dim]")

    except Exception as e:
        console.print(f"\\n[red]✖ Failed to create connection:[/red] {str(e)}")


@connection.command("list")
def list():
    """List available database connections.

    Examples:

        kai connection list
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    connections = db_repo.find_all()

    if not connections:
        console.print("[yellow]No database connections found[/yellow]")
        return

    console.print("[bold]Available Connections:[/bold]")
    for conn in connections:
        console.print(f"  {conn.id}: {conn.alias or conn.dialect} ({conn.dialect})")


@connection.command("show")
@click.argument("db_connection_id")
def show(db_connection_id: str):
    """Show details of a database connection.

    Examples:

        kai connection show abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.utils.core.encrypt import FernetEncrypt
    from urllib.parse import urlparse

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    table_repo = TableDescriptionRepository(storage)

    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Decrypt URI to show host info (without password)
    fernet = FernetEncrypt()
    try:
        decrypted_uri = fernet.decrypt(db_connection.connection_uri)
        parsed = urlparse(decrypted_uri)
        safe_uri = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}"
        if parsed.port:
            safe_uri += f":{parsed.port}"
        safe_uri += parsed.path
    except Exception:
        safe_uri = "[encrypted]"

    # Get associated tables
    tables = table_repo.find_by({"db_connection_id": db_connection_id})

    console.print(Panel(
        f"[bold]ID:[/bold] {db_connection.id}\\n"
        f"[bold]Alias:[/bold] {db_connection.alias}\\n"
        f"[bold]Dialect:[/bold] {db_connection.dialect}\\n"
        f"[bold]Connection:[/bold] {safe_uri}\\n"
        f"[bold]Schemas:[/bold] {', '.join(db_connection.schemas)}\\n"
        f"[bold]Created:[/bold] {db_connection.created_at}\\n"
        f"[bold]Description:[/bold] {db_connection.description or 'N/A'}",
        title=f"Connection: {db_connection.alias}",
        border_style="cyan"
    ))

    if tables:
        console.print(f"\\n[bold]Associated Tables ({len(tables)}):[/bold]")
        for table in tables[:20]:
            status_color = "green" if table.sync_status == "SCANNED" else "yellow"
            console.print(f"  [{status_color}]●[/{status_color}] {table.db_schema}.{table.table_name} ({table.sync_status})")
        if len(tables) > 20:
            console.print(f"  [dim]... and {len(tables) - 20} more[/dim]")


@connection.command("update")
@click.argument("db_connection_id")
@click.option("--alias", "-a", help="New alias for the connection")
@click.option("--schema", "-s", "schemas", multiple=True, help="New schema(s) to use (replaces existing)")
@click.option("--metadata", "-m", type=str, help="JSON metadata for the connection")
@click.option("--uri", "-u", "connection_uri", help="New connection URI")
def update(db_connection_id: str, alias: str, schemas: tuple, metadata: str, connection_uri: str):
    """Update an existing database connection.

    Examples:

        kai connection update abc123 --alias new_name

        kai connection update abc123 --schema public --schema analytics

        kai connection update abc123 --uri "postgresql://newuser:pass@host/db"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import DatabaseConnectionRequest
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.utils.sql_database.scanner import SqlAlchemyScanner

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    scanner = SqlAlchemyScanner()
    service = DatabaseConnectionService(scanner, storage)

    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        raise click.Abort()

    # Build update request with only provided fields
    existing_uri = None
    try:
        from app.utils.core.encrypt import FernetEncrypt
        fernet = FernetEncrypt()
        existing_uri = fernet.decrypt(db_connection.connection_uri)
    except Exception:
        pass

    # Parse metadata if provided
    meta_dict = db_connection.metadata
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            raise click.Abort()

    request = DatabaseConnectionRequest(
        alias=alias or db_connection.alias,
        connection_uri=connection_uri or existing_uri,
        schemas=list(schemas) if schemas else db_connection.schemas,
        metadata=meta_dict,
    )

    console.print(f"[bold]Updating connection '{db_connection.alias}'...[/bold]")

    try:
        with console.status("[bold cyan]Updating connection and rescanning tables...[/bold cyan]"):
            updated_connection = service.update_database_connection(db_connection_id, request)

        console.print(f"\\n[green]✔ Connection updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated_connection.id}\\n"
            f"[bold]Alias:[/bold] {updated_connection.alias}\\n"
            f"[bold]Dialect:[/bold] {updated_connection.dialect}\\n"
            f"[bold]Schemas:[/bold] {', '.join(updated_connection.schemas)}",
            title="Updated Connection",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\\n[red]✖ Failed to update connection:[/red] {str(e)}")


@connection.command("delete")
@click.argument("connection_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(connection_id: str, force: bool):
    """Delete a database connection.

    CONNECTION_ID: Connection ID or alias to delete

    Examples:

        kai connection delete conn_123

        kai connection delete production -f
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService

    storage = Storage(Settings())
    db_repo = DatabaseConnectionRepository(storage)
    service = DatabaseConnectionService(storage)

    # Find connection by ID or alias
    conn = db_repo.find_by_id(connection_id)
    if not conn:
        # Try to find by alias
        all_conns = db_repo.find_all()
        conn = next((c for c in all_conns if c.alias == connection_id), None)

    if not conn:
        console.print(f"[red]Error:[/red] Connection '{connection_id}' not found")
        console.print("\\nAvailable connections:")
        for c in all_conns:
            console.print(f"  {c.id}: {c.alias} ({c.dialect})")
        raise click.Abort()

    # Confirm unless forced
    if not force:
        console.print(f"[yellow]About to delete connection:[/yellow]")
        console.print(f"  ID: {conn.id}")
        console.print(f"  Alias: {conn.alias}")
        console.print(f"  Dialect: {conn.dialect}")
        if not click.confirm("\\nDo you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        deleted = service.delete_database_connection(conn.id)
        console.print(Panel(
            f"[bold green]✔ Connection deleted[/bold green]\\n\\n"
            f"[cyan]Alias:[/cyan] {deleted.alias}\\n"
            f"[cyan]ID:[/cyan] {deleted.id}",
            title="Connection Deleted",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]Error deleting connection:[/red] {e}")
        raise click.Abort()


@connection.command("test")
@click.argument("connection_uri")
def test(connection_uri: str):
    """Test a database connection without saving it.

    Examples:

        kai connection test "postgresql://user:pass@localhost:5432/mydb"

        kai connection test "csv://path/to/data.csv"
    """
    from app.utils.sql_database.sql_database import SQLDatabase

    console.print(f"[bold]Testing connection...[/bold]")
    console.print(f"[dim]URI: {connection_uri[:50]}...[/dim]" if len(connection_uri) > 50 else f"[dim]URI: {connection_uri}[/dim]")

    try:
        with console.status("[bold cyan]Connecting...[/bold cyan]"):
            sql_database = SQLDatabase.from_uri(connection_uri)
            # Test the connection
            sql_database.engine.connect()

            # Get tables
            from sqlalchemy import inspect
            inspector = inspect(sql_database.engine)
            tables = inspector.get_table_names()
            views = inspector.get_view_names()

        console.print(f"\\n[green]✔ Connection successful![/green]")
        console.print(f"[bold]Dialect:[/bold] {sql_database.dialect}")
        console.print(f"[bold]Tables found:[/bold] {len(tables)}")
        if tables:
            console.print(f"  {', '.join(tables[:10])}" + ("..." if len(tables) > 10 else ""))
        if views:
            console.print(f"[bold]Views found:[/bold] {len(views)}")
            console.print(f"  {', '.join(views[:10])}" + ("..." if len(views) > 10 else ""))

    except Exception as e:
        console.print(f"\\n[red]✖ Connection failed:[/red] {str(e)}")
