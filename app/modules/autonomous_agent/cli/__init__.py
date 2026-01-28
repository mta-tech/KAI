"""KAI CLI shared utilities and group registration.

This module contains shared utilities used across all CLI command groups,
and handles registration of command groups with the main CLI.
"""

import asyncio
import socket
import subprocess
import click
from rich.console import Console

console = Console()


def check_typesense_running() -> bool:
    """Check if Typesense is running and accessible.

    Returns:
        True if Typesense is available, False otherwise
    """
    # First try: check if Typesense container is running
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", "typesense"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "running" in result.stdout:
            return True
    except Exception:
        pass

    # Fallback: try to connect to the port
    try:
        settings = None
        try:
            from app.server.config import Settings
            settings = Settings()
            typesense_host = settings.TYPESENSE_HOST
        except Exception:
            typesense_host = "localhost"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((typesense_host, 8108))
        sock.close()
        return result == 0
    except Exception:
        pass

    return False


def offer_typesense_deployment() -> bool:
    """Offer to deploy Typesense if not running.

    Returns:
        True if Typesense was started successfully, False otherwise
    """
    import time

    console.print("\n[yellow]⚠ Typesense is not running or not accessible[/yellow]")
    console.print("[dim]Typesense is required for most KAI operations.[/dim]")
    console.print()

    if not click.confirm("Would you like to start Typesense now?", default=True):
        return False

    console.print("\n[cyan]Starting Typesense with Docker Compose...[/cyan]")

    try:
        # Run docker compose up typesense -d
        result = subprocess.run(
            ["docker", "compose", "up", "typesense", "-d"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            console.print("[green]✔ Typesense started successfully![/green]")

            # Wait a moment for Typesense to be ready
            console.print("[dim]Waiting for Typesense to be ready...[/dim]")
            time.sleep(3)

            if check_typesense_running():
                console.print("[green]✔ Typesense is ready![/green]\n")
                return True
            else:
                console.print("[yellow]⚠ Typesense started but not yet accessible. You may need to wait a few moments.[/yellow]")
                return True
        else:
            console.print(f"[red]✖ Failed to start Typesense:[/red] {result.stderr}")
            console.print("[dim]Please run manually: docker compose up typesense -d[/dim]")
            return False

    except subprocess.TimeoutExpired:
        console.print("[red]✖ Timeout starting Typesense[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]✖ Docker not found. Please install Docker or start Typesense manually.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✖ Error starting Typesense:[/red] {e}")
        return False


def ensure_typesense_or_prompt(required: bool = True) -> bool:
    """Check Typesense is running, offer to deploy if not.

    Args:
        required: If True, exit when Typesense not available

    Returns:
        True if Typesense is available, False otherwise
    """
    if check_typesense_running():
        return True

    if not required:
        return False

    if offer_typesense_deployment():
        return check_typesense_running()

    console.print("[yellow]⚠ Cannot proceed without Typesense[/yellow]")
    return False


def _run_async(coro):
    """Bridge async functions in synchronous Click context.

    Click commands are synchronous, but KAI services are async.
    This wrapper bridges the gap by running the coroutine in an event loop.

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of async operation
    """
    return asyncio.run(coro)


def resolve_db_identifier(identifier: str, repo):
    """Resolve database identifier (ID or alias) to connection.

    Tries to find a database connection by alias first, then by ID.
    This provides a better user experience as users typically work with
    friendly aliases rather than UUIDs.

    Args:
        identifier: Connection ID (UUID) or database alias
        repo: DatabaseConnectionRepository instance

    Returns:
        DatabaseConnection object or None if not found
    """
    # Try alias first (more user-friendly)
    db_conn = repo.find_by_alias(identifier)
    if db_conn:
        return db_conn

    # Try ID
    db_conn = repo.find_by_id(identifier)
    return db_conn
