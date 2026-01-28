"""Session management commands for KAI Autonomous Agent.

This module provides commands for managing conversation sessions:
- List and search sessions
- Show detailed session information
- Export sessions to JSON or Markdown
- Delete individual sessions
- Clear all sessions
"""
import asyncio
import json

import click

from app.modules.autonomous_agent.cli import (
    _run_async,
    console,
    ensure_typesense_or_prompt,
)

# ============================================================================
# Session Command Group
# ============================================================================

@click.group()
def session():
    """Session management commands - list, show, export, and delete conversation sessions."""
    pass


# ============================================================================
# List Sessions
# ============================================================================

@session.command("list")
@click.option("--db", "db_connection_id", help="Filter by database connection ID")
@click.option("--status", type=click.Choice(["idle", "processing", "error", "closed"]), help="Filter by status")
@click.option("--limit", "-l", default=50, help="Maximum number of sessions to show")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed session info")
def list_sessions(db_connection_id: str | None, status: str | None, limit: int, verbose: bool):
    """List all conversation sessions.

    Examples:

        kai session list

        kai session list --db conn_123

        kai session list --status idle --limit 10

        kai session list -v  # Detailed view
    """
    _run_async(_list_sessions(db_connection_id, status, limit, verbose))


async def _list_sessions(db_connection_id: str | None, status: str | None, limit: int, verbose: bool):
    """List sessions implementation."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.session import SessionRepository, SessionStatus
    from rich.table import Table
    from datetime import datetime

    settings = Settings()
    storage = Storage(settings)
    repo = SessionRepository(storage)

    # Convert status string to enum if provided
    status_filter = SessionStatus(status) if status else None

    sessions = await repo.list(
        db_connection_id=db_connection_id,
        status=status_filter,
        limit=limit
    )

    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return

    table = Table(title=f"Sessions ({len(sessions)})")
    table.add_column("ID", style="cyan")
    table.add_column("Database", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Messages", style="magenta", justify="right")
    table.add_column("Updated", style="dim")

    if verbose:
        table.add_column("Summary", style="dim", max_width=40)

    for session in sessions:
        # Format timestamp
        if isinstance(session.updated_at, datetime):
            updated = session.updated_at.strftime("%Y-%m-%d %H:%M")
        else:
            updated = str(session.updated_at)[:16]

        row = [
            session.id[:20] + "..." if len(session.id) > 20 else session.id,
            session.db_connection_id[:15] + "..." if len(session.db_connection_id) > 15 else session.db_connection_id,
            session.status.value,
            str(len(session.messages)),
            updated,
        ]

        if verbose:
            summary = session.summary or "(no summary)"
            if len(summary) > 40:
                summary = summary[:37] + "..."
            row.append(summary)

        table.add_row(*row)

    console.print(table)


# ============================================================================
# Show Session
# ============================================================================

@session.command("show")
@click.argument("session_id")
def show_session(session_id: str):
    """Show details of a specific session.

    Examples:

        kai session show sess_abc123

        kai session show brave-falcon-472
    """
    _run_async(_show_session(session_id))


async def _show_session(session_id: str):
    """Show session details implementation."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.session import SessionRepository
    from rich.panel import Panel
    from rich.table import Table

    settings = Settings()
    storage = Storage(settings)
    repo = SessionRepository(storage)

    session = await repo.get(session_id)

    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return

    # Session metadata panel
    info = [
        f"[bold]ID:[/bold] {session.id}",
        f"[bold]Database:[/bold] {session.db_connection_id}",
        f"[bold]Status:[/bold] {session.status.value}",
        f"[bold]Messages:[/bold] {len(session.messages)}",
        f"[bold]Created:[/bold] {session.created_at}",
        f"[bold]Updated:[/bold] {session.updated_at}",
    ]

    if session.summary:
        info.append(f"[bold]Summary:[/bold] {session.summary}")

    if session.metadata:
        info.append(f"[bold]Metadata:[/bold] {json.dumps(session.metadata, indent=2)}")

    console.print(Panel("\n".join(info), title="Session Details", border_style="cyan"))

    # Messages table
    if session.messages:
        console.print("\n[bold]Conversation History:[/bold]\n")

        for msg in session.messages:
            role_color = "blue" if msg.role == "human" else "green"
            role_label = "You" if msg.role == "human" else "KAI"

            console.print(f"[{role_color}][bold]{role_label}:[/bold][/{role_color}] {msg.query[:100]}{'...' if len(msg.query) > 100 else ''}")

            if msg.sql:
                console.print(f"  [dim]SQL: {msg.sql[:80]}{'...' if len(msg.sql) > 80 else ''}[/dim]")

            if msg.analysis:
                analysis_preview = msg.analysis[:100] + "..." if len(msg.analysis) > 100 else msg.analysis
                console.print(f"  [dim]Analysis: {analysis_preview}[/dim]")

            console.print()


# ============================================================================
# Export Session
# ============================================================================

@session.command("export")
@click.argument("session_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: session_<id>.json)")
@click.option("--format", "-f", "output_format", type=click.Choice(["json", "markdown"]), default="json", help="Export format")
def export_session(session_id: str, output: str | None, output_format: str):
    """Export a session to file.

    Examples:

        kai session export sess_abc123

        kai session export brave-falcon-472 -o my_session.json

        kai session export sess_abc123 -f markdown -o conversation.md
    """
    _run_async(_export_session(session_id, output, output_format))


async def _export_session(session_id: str, output: str | None, output_format: str):
    """Export session implementation."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.session import SessionRepository

    settings = Settings()
    storage = Storage(settings)
    repo = SessionRepository(storage)

    session = await repo.get(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return

    # Determine output file
    if not output:
        ext = "md" if output_format == "markdown" else "json"
        output = f"session_{session_id.replace('-', '_')}.{ext}"

    if output_format == "json":
        content = json.dumps(session.to_dict(), indent=2, default=str)
    else:
        # Markdown format
        lines = [
            f"# Session: {session_id}",
            "",
            f"**Database:** {session.db_connection_id}",
            f"**Status:** {session.status.value}",
            f"**Created:** {session.created_at}",
            f"**Updated:** {session.updated_at}",
            "",
        ]

        if session.summary:
            lines.extend([f"**Summary:** {session.summary}", ""])

        lines.extend(["---", "", "## Conversation", ""])

        for msg in session.messages:
            role = "**You:**" if msg.role == "human" else "**KAI:**"
            lines.append(f"{role} {msg.query}")
            lines.append("")

            if msg.sql:
                lines.extend(["```sql", msg.sql, "```", ""])

            if msg.analysis:
                lines.extend([msg.analysis, ""])

            lines.append("---")
            lines.append("")

        content = "\n".join(lines)

    with open(output, "w") as f:
        f.write(content)

    console.print(f"[green]✔ Session exported to:[/green] {output}")
    console.print(f"[dim]Messages: {len(session.messages)} | Format: {output_format}[/dim]")


# ============================================================================
# Delete Session
# ============================================================================

@session.command("delete")
@click.argument("session_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_session(session_id: str, force: bool):
    """Delete a session.

    Examples:

        kai session delete sess_abc123

        kai session delete brave-falcon-472 -f
    """
    _run_async(_delete_session(session_id, force))


async def _delete_session(session_id: str, force: bool):
    """Delete session implementation."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.session import SessionRepository

    settings = Settings()
    storage = Storage(settings)
    repo = SessionRepository(storage)

    # Check if session exists
    session = await repo.get(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return

    if not force:
        console.print(f"[yellow]About to delete session:[/yellow] {session_id}")
        console.print(f"  Messages: {len(session.messages)}")
        console.print(f"  Database: {session.db_connection_id}")
        if not click.confirm("Are you sure you want to delete this session?"):
            console.print("[dim]Cancelled[/dim]")
            return

    await repo.delete(session_id)
    console.print(f"[green]✔ Session deleted:[/green] {session_id}")


# ============================================================================
# Clear Sessions
# ============================================================================

@session.command("clear")
@click.option("--db", "db_connection_id", help="Filter by database connection ID")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def clear_sessions(db_connection_id: str | None, force: bool):
    """Clear all sessions (optionally for a specific database).

    Examples:

        kai session clear

        kai session clear --db conn_123

        kai session clear -f  # Skip confirmation
    """
    _run_async(_clear_sessions(db_connection_id, force))


async def _clear_sessions(db_connection_id: str | None, force: bool):
    """Clear sessions implementation."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.session import SessionRepository

    settings = Settings()
    storage = Storage(settings)
    repo = SessionRepository(storage)

    sessions = await repo.list(db_connection_id=db_connection_id, limit=1000)

    if not sessions:
        console.print("[yellow]No sessions to clear[/yellow]")
        return

    if not force:
        if db_connection_id:
            console.print(f"[yellow]About to delete {len(sessions)} sessions for database: {db_connection_id}[/yellow]")
        else:
            console.print(f"[yellow]About to delete ALL {len(sessions)} sessions[/yellow]")

        if not click.confirm("Are you sure you want to delete these sessions?"):
            console.print("[dim]Cancelled[/dim]")
            return

    deleted = 0
    for session in sessions:
        await repo.delete(session.id)
        deleted += 1

    console.print(f"[green]✔ Deleted {deleted} sessions[/green]")
