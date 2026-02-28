"""CLI for KAI Autonomous Agent - Intelligent Business Advisor.

Usage:
    # Complete query workflow example
    kai connection create "postgresql://user:pass@host:5432/db" -a mydb
    kai table scan-all mydb -d
    kai query run "Analyze sales by region" --db mydb
    kai session list --db mydb

    # Run analysis queries
    kai query run "Analyze sales by region" --db conn_123
    kai query run "Show top customers" --db conn_123 --mode query
    kai query interactive --db conn_123
    kai query resume sess_abc123 "Continue the analysis" --db conn_123
    kai query debug sess_abc123 --db conn_123

    # Database connection management
    kai connection list
    kai connection test "postgresql://user:pass@host:5432/db"
    kai connection create "postgresql://user:pass@host:5432/db" -a my_database
    kai connection create "postgresql://user:pass@host:5432/db" -a my_db -s public -s analytics
    kai connection show <connection_id>
    kai connection update <connection_id> --alias new_name
    kai connection delete <connection_id>

    # Table management
    kai table list <connection_id>
    kai table show <table_id>
    kai table refresh <connection_id>
    kai table scan <connection_id>
    kai table scan <connection_id> --with-descriptions --model-family openai
    kai table scan-all <connection_id>              # Refresh + scan all tables
    kai table scan-all <connection_id> -d --model-family openai  # With AI descriptions
    kai table context <connection_id>               # Display schema info
    kai table context <connection_id> -s -d         # With samples + DDL
    kai table context <connection_id> -f markdown -o context.md  # Export
    kai table search <connection_id> "kpi"          # Search for 'kpi' anywhere
    kai table search <connection_id> "*_id"         # Columns ending with _id
    kai table search <connection_id> "user*" -i columns  # Search only column names
    kai table search <connection_id> "revenue" -i descriptions  # Search descriptions

    # Knowledge management
    kai knowledge glossary add <connection_id> --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"
    kai knowledge glossary list <connection_id>
    kai knowledge glossary show <glossary_id>
    kai knowledge glossary update <glossary_id> --sql "SELECT SUM(amount) FROM orders WHERE status='completed'"
    kai knowledge glossary delete <glossary_id>
    kai knowledge instruction add <connection_id> --category "Always" --rule "Format currency with $"
    kai knowledge instruction list <connection_id>
    kai knowledge instruction show <instruction_id>
    kai knowledge instruction update <instruction_id> --rule "New rules"
    kai knowledge instruction delete <instruction_id>

    # Skills management (to be refactored to 'kai skill' group)
    kai-agent discover-skills <connection_id> --path ./.skills
    kai-agent list-skills <connection_id>
    kai-agent show-skill <connection_id> <skill_id>
    kai-agent search-skills <connection_id> "revenue analysis"
    kai-agent reload-skill <connection_id> <skill_id> --path ./.skills
    kai-agent delete-skill <connection_id> <skill_id>

    # Memory management (conversation history and context)
    kai knowledge memory list <connection_id>
    kai knowledge memory list <connection_id> --namespace user_preferences
    kai knowledge memory search "date format preferences" -d <connection_id>
    kai knowledge memory add <connection_id> user_preferences date_format "Use YYYY-MM-DD"
    kai knowledge memory delete <connection_id> user_preferences old_format
    kai knowledge memory clear <connection_id> --namespace user_preferences
    kai knowledge memory namespaces <connection_id>

    # Session management (conversation history)
    kai session list                                      # List all sessions
    kai session list --db conn_123                        # Filter by database
    kai session list --status idle                        # Filter by status
    kai session show <session_id>                         # View session details
    kai session delete <session_id>                       # Delete a session
    kai session export <session_id> -o chat.json          # Export to JSON
    kai session export <session_id> -f markdown           # Export to Markdown
    kai session clear                                     # Delete all sessions
    kai session clear --db conn_123                       # Delete sessions for DB

    # Configuration & diagnostics
    kai config show                                       # Show current config
    kai config show --json                                # Output as JSON
    kai-agent env-check                                   # Validate environment (to be refactored)
    kai-agent version                                     # Show version info (to be refactored)

    # MDL (semantic layer) management
    kai mdl list                                          # List all MDL manifests
    kai mdl list --db koperasi                            # List MDLs for a database
    kai mdl show <manifest_id>                            # Show manifest details
    kai mdl show <manifest_id> --summary                   # Show summary only
    kai mdl show <manifest_id> -f json                     # Export as JSON
    kai mdl show <manifest_id> -f markdown -o file.md     # Export as Markdown

Note: Many commands have been reorganized into command groups for better organization.
Run 'kai --help' to see all available groups, or 'kai <group> --help' for group-specific commands.
Commands still using 'kai-agent' will be refactored in future phases.
"""
import asyncio
import json
import uuid
import random
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.markup import escape as escape_markup
from rich.text import Text
from rich.spinner import Spinner

console = Console()

# Import command groups
from app.modules.autonomous_agent.cli.benchmark import benchmark
from app.modules.autonomous_agent.cli.config import config
from app.modules.autonomous_agent.cli.connection import connection
from app.modules.autonomous_agent.cli.context import context
from app.modules.autonomous_agent.cli.dashboard import dashboard
from app.modules.autonomous_agent.cli.knowledge import knowledge
from app.modules.autonomous_agent.cli.mdl import mdl
from app.modules.autonomous_agent.cli.query import query
from app.modules.autonomous_agent.cli.session import session
from app.modules.autonomous_agent.cli.table import table

# Word lists for human-readable session IDs
ADJECTIVES = [
    "amber", "azure", "bold", "brave", "bright", "calm", "clear", "cool",
    "coral", "crisp", "dawn", "deep", "eager", "early", "fair", "fast",
    "fine", "fond", "free", "fresh", "gold", "good", "grand", "green",
    "happy", "keen", "kind", "late", "light", "live", "lunar", "mild",
    "neat", "noble", "pale", "pure", "quick", "quiet", "rapid", "rare",
    "rich", "royal", "safe", "sharp", "silver", "sleek", "smart", "smooth",
    "solar", "solid", "sonic", "steady", "still", "strong", "sunny", "super",
    "sweet", "swift", "teal", "true", "vivid", "warm", "wild", "wise",
]

NOUNS = [
    "anchor", "arrow", "atlas", "aurora", "badge", "beacon", "bird", "blaze",
    "bloom", "bolt", "bridge", "brook", "castle", "cedar", "cliff", "cloud",
    "comet", "coral", "crane", "creek", "crown", "crystal", "delta", "dune",
    "eagle", "ember", "falcon", "fern", "flame", "forest", "frost", "garden",
    "glacier", "grove", "harbor", "hawk", "horizon", "island", "jasmine", "lake",
    "leaf", "lion", "lotus", "maple", "meadow", "moon", "mountain", "oak",
    "ocean", "olive", "orchid", "palm", "peak", "pearl", "phoenix", "pine",
    "planet", "pond", "prairie", "rain", "raven", "reef", "ridge", "river",
    "robin", "rose", "sage", "shore", "sky", "snow", "sparrow", "spring",
    "star", "stone", "storm", "stream", "summit", "sun", "thunder", "tide",
    "tiger", "trail", "tree", "tulip", "valley", "wave", "willow", "wind",
]


def generate_session_id() -> str:
    """Generate a unique human-readable session ID like 'amber-falcon-472'."""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    # Add 3-digit suffix for uniqueness (5,632 × 1000 = 5.6M combinations)
    suffix = random.randint(100, 999)
    return f"{adjective}-{noun}-{suffix}"



# ============================================================================
# Typesense Health Check
# ============================================================================

def check_typesense_running() -> bool:
    """Check if Typesense is running and accessible."""
    import subprocess
    try:
        # Check if Typesense container is running
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
    import socket
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
    """Offer to deploy Typesense if not running."""
    import subprocess

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
            import time
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

    Returns True if Typesense is available, False otherwise.
    """
    if check_typesense_running():
        return True

    if not required:
        return False

    if offer_typesense_deployment():
        return check_typesense_running()

    console.print("[yellow]⚠ Cannot proceed without Typesense[/yellow]")
    return False

@click.group()
def cli():
    """KAI Autonomous Agent - AI-powered data analysis."""
    pass

# Register command groups
cli.add_command(benchmark)
cli.add_command(context)
cli.add_command(config)
cli.add_command(connection)
cli.add_command(dashboard)
cli.add_command(knowledge)
cli.add_command(mdl)
cli.add_command(query)
cli.add_command(session)
cli.add_command(table)


if __name__ == "__main__":
    cli()
