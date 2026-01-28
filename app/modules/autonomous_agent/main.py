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

    # Business glossary management (to be refactored to 'kai glossary' group)
    kai-agent add-glossary <connection_id> --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"
    kai-agent add-glossary <connection_id> -m "MRR" -s "SELECT SUM(amount) FROM subscriptions WHERE status='active'" --alias "Monthly Recurring Revenue"
    kai-agent list-glossaries <connection_id>
    kai-agent show-glossary <glossary_id>
    kai-agent update-glossary <glossary_id> --sql "SELECT SUM(amount) FROM orders WHERE status='completed'"
    kai-agent delete-glossary <glossary_id>

    # Custom instructions management (to be refactored to 'kai instruction' group)
    kai-agent add-instruction <connection_id> -c "Always" -r "Format currency with $" --default
    kai-agent add-instruction <connection_id> -c "When asked about revenue" -r "Use revenue_by_month view"
    kai-agent list-instructions <connection_id>
    kai-agent list-instructions <connection_id> --type default
    kai-agent show-instruction <instruction_id>
    kai-agent update-instruction <instruction_id> --rules "New rules"
    kai-agent delete-instruction <instruction_id>

    # Skills management (to be refactored to 'kai skill' group)
    kai-agent discover-skills <connection_id> --path ./.skills
    kai-agent list-skills <connection_id>
    kai-agent show-skill <connection_id> <skill_id>
    kai-agent search-skills <connection_id> "revenue analysis"
    kai-agent reload-skill <connection_id> <skill_id> --path ./.skills
    kai-agent delete-skill <connection_id> <skill_id>

    # Memory management (to be refactored to 'kai memory' group)
    kai-agent list-memories <connection_id>
    kai-agent list-memories <connection_id> --namespace user_preferences
    kai-agent show-memory <connection_id> <namespace> <key>
    kai-agent search-memories <connection_id> "date format preferences"
    kai-agent add-memory <connection_id> user_preferences date_format "Use YYYY-MM-DD"
    kai-agent delete-memory <connection_id> <namespace> <key>
    kai-agent clear-memories <connection_id> --namespace user_preferences
    kai-agent list-namespaces <connection_id>

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
from app.modules.autonomous_agent.cli.config import config
from app.modules.autonomous_agent.cli.connection import connection

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
cli.add_command(config)
cli.add_command(connection)


@cli.command()
@click.argument("prompt")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option(
    "--mode",
    type=click.Choice(["full_autonomy", "analysis", "query", "script"]),
    default="full_autonomy",
    help="Agent operation mode",
)
@click.option("--output", "-o", type=click.Path(), help="Save result to file")
@click.option("--stream/--no-stream", default=True, help="Stream output")
def run(prompt: str, db_connection_id: str, mode: str, output: str, stream: bool):
    """Run an autonomous analysis task.

    Examples:

        kai-agent run "What are the top 10 products by revenue?" --db conn_123

        kai-agent run "Analyze customer churn patterns" --db conn_123 --mode analysis

        kai-agent run "Continue the analysis" --db conn_123 --session sess_abc123def456
    """
    asyncio.run(_run_task(prompt, db_connection_id, mode, output, stream))


@cli.command()
@click.argument("session_id")
@click.argument("prompt")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option(
    "--mode",
    type=click.Choice(["full_autonomy", "analysis", "query", "script"]),
    default="full_autonomy",
    help="Agent operation mode",
)
@click.option("--output", "-o", type=click.Path(), help="Save result to file")
@click.option("--stream/--no-stream", default=True, help="Stream output")
def resume(session_id: str, prompt: str, db_connection_id: str, mode: str, output: str, stream: bool):
    """Resume an existing session with a new prompt.

    SESSION_ID is the session ID from a previous run (e.g., sess_abc123def456).

    Examples:

        kai-agent resume sess_abc123def456 "Continue analyzing the data" --db conn_123

        kai-agent resume sess_abc123def456 "What else can you tell me?" --db conn_123
    """
    asyncio.run(_run_task(prompt, db_connection_id, mode, output, stream))


def _render_todos(todos: list) -> Panel | None:
    """Render todos as a Rich Panel."""
    if not todos:
        return None

    todo_lines = []
    for todo in todos:
        status = todo.get('status', 'pending')
        content = todo.get('content', '')
        # Escape content to prevent Rich markup parsing errors
        escaped_content = escape_markup(content)
        if status == 'completed':
            icon = "[green]✔[/green]"
            style = "strike dim"
        elif status == 'in_progress':
            icon = "[blue]➜[/blue]"
            style = "bold"
        else:
            icon = "[yellow]○[/yellow]"
            style = ""
        
        if style:
            todo_lines.append(f"{icon} [{style}]{escaped_content}[/{style}]")
        else:
            todo_lines.append(f"{icon} {escaped_content}")

    if todo_lines:
        return Panel("\n".join(todo_lines), title="📋 Progress", border_style="magenta", title_align="left")
    return None


async def _render_stream(service, task, console):
    """Helper to stream and render agent events."""
    output_text = ""
    agent_stack = ["KAI"] # Track active agent context
    
    # Track todos for nice display
    current_todos = []
    
    with Live(console=console, refresh_per_second=10, vertical_overflow="visible") as live:
        async for event in service.stream_execute(task):
            if event["type"] == "token":
                output_text += event["content"]
                live.update(Markdown(output_text))
            
            elif event["type"] == "todo_update":
                # Update our local list of todos
                # todos structure is list of dicts: [{'content': '...', 'status': 'pending'/'completed'/'in_progress', ...}]
                new_todos = event.get("todos", [])
                if new_todos:
                    current_todos = new_todos
                    # Render the todo list
                    todo_lines = []
                    for todo in current_todos:
                        status = todo.get('status', 'pending')
                        content = todo.get('content', '')
                        if status == 'completed':
                            icon = "[green]✔[/green]"
                            style = "strike dim"
                        elif status == 'in_progress':
                            icon = "[blue]➜[/blue]"
                            style = "bold"
                        else:
                            icon = "[yellow]○[/yellow]"
                            style = ""
                        
                        todo_lines.append(f"{icon} [{style}]{content}[/{style}]")
                    
                    if todo_lines:
                        console.print(Panel("\n".join(todo_lines), title="Todo List", border_style="magenta", title_align="left"))

            elif event["type"] == "tool_start":
                # Flush reasoning/thought block if exists
                if output_text.strip():
                    current_agent = agent_stack[-1]
                    title = "Reasoning" if current_agent == "KAI" else f"{current_agent} Reasoning"
                    style = "yellow" if current_agent == "KAI" else "blue"
                    
                    # Print ABOVE the live display area
                    console.print(Panel(Markdown(output_text), title=title, border_style=style, title_align="left"))
                    output_text = ""
                    live.update(Markdown("")) # Clear live area for next phase

                tool_name = event['tool']
                tool_input = event.get('input')
                
                if tool_name == "task":
                    # This is a subagent call
                    agent_name = tool_input.get("agent") or tool_input.get("name") or "subagent"
                    agent_stack.append(agent_name)
                    
                    prompt = tool_input.get("prompt", "")
                    console.print(f"\n[bold blue]➤ Delegating to {agent_name}[/bold blue]")
                    # Use a Panel for the prompt to ensure it's clearly visible even if multi-line
                    console.print(Panel(Markdown(prompt), title=f"{agent_name} Task", border_style="blue", title_align="left"))
                elif tool_name == "write_todos":
                    # We handle todo updates via the dedicated event type, but we can acknowledge the tool call briefly
                    pass 
                else:
                    # Normal tool call
                    prefix = "  " * (len(agent_stack) - 1)
                    console.print(f"\n{prefix}[bold cyan]➜ Calling tool: {tool_name}[/bold cyan]")
                    if tool_input:
                        if isinstance(tool_input, dict):
                            # Pretty print args
                            for k, v in tool_input.items():
                                console.print(f"{prefix}[dim]  {k}: {v}[/dim]")
                        else:
                            console.print(f"{prefix}[dim]  Input: {tool_input}[/dim]")
            
            elif event["type"] == "tool_end":
                tool_name = event['tool']
                output = event.get('output', '')
                
                if tool_name == "task":
                    finished_agent = agent_stack.pop() if len(agent_stack) > 1 else "subagent"
                    console.print(f"[bold green]✔ {finished_agent} completed[/bold green]")
                    # Show subagent result
                    console.print(Panel(Markdown(output), title=f"{finished_agent} Result", border_style="blue", title_align="left"))
                elif tool_name == "write_todos":
                    # Skip printing result for write_todos to reduce noise, as we render the list
                    pass
                else:
                    prefix = "  " * (len(agent_stack) - 1)
                    # Truncate long outputs for display but show success
                    display_output = output[:500] + "..." if len(output) > 500 else output
                    console.print(f"{prefix}[bold green]✔ {tool_name} result:[/bold green]")
                    console.print(f"{prefix}[dim]{display_output}[/dim]")

        # End of stream - Final Result
        if output_text.strip():
            # Clear the live component one last time
            live.update(Markdown(""))
            # Print the final result as a distinct panel
            console.print(Panel(Markdown(output_text), title="Analysis / Result", border_style="green", title_align="left"))

async def _run_task(
    prompt: str, db_connection_id: str, mode: str, output: str, stream: bool
):
    """Execute agent task."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.autonomous_agent.service import AutonomousAgentService
    from app.modules.autonomous_agent.models import AgentTask
    from app.utils.sql_database.sql_database import SQLDatabase
    from app.utils.core.encrypt import FernetEncrypt
    from urllib.parse import unquote
    from app.modules.sql_generation.models import LLMConfig

    # Initialize
    settings = Settings()
    storage = Storage(settings)
    db_repo = DatabaseConnectionRepository(storage)
    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Error:[/red] Database connection '{db_connection_id}' not found")
        return

    # Configure LLM
    llm_config = LLMConfig(
        model_family=settings.CHAT_FAMILY,
        model_name=settings.CHAT_MODEL,
    )

    # Patch connection for CLI use (host networking)
    fernet = FernetEncrypt()
    try:
        decrypted_uri = unquote(fernet.decrypt(db_connection.connection_uri))
        if "postgres-warehouse" in decrypted_uri:
            console.print("[dim]Patching connection for local CLI execution...[/dim]")
            # Replace host and port
            # Standard URI: postgresql://user:pass@host:port/db
            patched_uri = decrypted_uri.replace("postgres-warehouse", "localhost")
            # If port 5432 is explicit, change to 5433.
            # If implicit, we might need to insert :5433
            if ":5432" in patched_uri:
                patched_uri = patched_uri.replace(":5432", ":5433")
            elif "@localhost/" in patched_uri:
                 patched_uri = patched_uri.replace("@localhost/", "@localhost:5433/")
            
            # Re-encrypt
            db_connection.connection_uri = fernet.encrypt(patched_uri)
            
            # Also patch alias to force new connection creation in pool
            db_connection.id = db_connection.id + "_cli_patched"
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to patch connection URI: {e}[/yellow]")

    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(db_connection, database, llm_config=llm_config)

    task = AgentTask(
        id=f"cli_{uuid.uuid4().hex[:8]}",
        prompt=prompt,
        db_connection_id=db_connection_id,
        mode=mode,
    )

    console.print(Panel(f"[bold]{prompt}[/bold]", title=f"KAI Agent [{mode}]"))

    if stream:
        # Streaming execution using new renderer
        await _render_stream(service, task, console)
    else:
        # Non-streaming execution
        with console.status("[bold]Thinking...[/bold]"):
            result = await service.execute(task)

        if result.status == "completed":
            console.print(Panel(Markdown(result.final_answer), title="Result", border_style="green"))
            console.print(f"[green]Completed in {result.execution_time_ms}ms[/green]")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

        if output and result.final_answer:
            with open(output, "w") as f:
                f.write(result.final_answer)
            console.print(f"[dim]Saved to {output}[/dim]")


@cli.command()
@click.option("--db", "db_identifier", required=True, help="Database connection ID or alias")
def interactive(db_identifier: str):
    """Start an interactive agent session.

    Example:
        kai interactive --db kemenkop
        kai interactive --db conn_123
    """
    asyncio.run(_interactive_session(db_identifier))


async def _interactive_session(db_identifier: str):
    """Interactive REPL session."""
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.autonomous_agent.service import AutonomousAgentService
    from app.modules.autonomous_agent.models import AgentTask
    from app.utils.sql_database.sql_database import SQLDatabase
    from app.utils.core.encrypt import FernetEncrypt
    from urllib.parse import unquote
    from app.modules.sql_generation.models import LLMConfig
    from langgraph.checkpoint.memory import MemorySaver

    settings = Settings()
    storage = Storage(settings)
    db_repo = DatabaseConnectionRepository(storage)
    
    # Try finding by alias first, then by ID
    db_connection = db_repo.find_by_alias(db_identifier)
    if not db_connection:
        db_connection = db_repo.find_by_id(db_identifier)

    if not db_connection:
        console.print(f"[red]Database connection '{db_identifier}' not found[/red]")
        return

    db_connection_id = db_connection.id

    # Configure LLM
    llm_config = LLMConfig(
        model_family=settings.CHAT_FAMILY,
        model_name=settings.CHAT_MODEL,
    )

    # Patch connection for CLI use (host networking)
    fernet = FernetEncrypt()
    try:
        decrypted_uri = unquote(fernet.decrypt(db_connection.connection_uri))
        if "postgres-warehouse" in decrypted_uri:
            console.print("[dim]Patching connection for local CLI execution...[/dim]")
            patched_uri = decrypted_uri.replace("postgres-warehouse", "localhost")
            if ":5432" in patched_uri:
                patched_uri = patched_uri.replace(":5432", ":5433")
            elif "@localhost/" in patched_uri:
                 patched_uri = patched_uri.replace("@localhost/", "@localhost:5433/")
            
            db_connection.connection_uri = fernet.encrypt(patched_uri)
            db_connection.id = db_connection.id + "_cli_patched"
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to patch connection URI: {e}[/yellow]")

    # Create memory checkpointer for multi-turn conversation
    checkpointer = MemorySaver()

    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(
        db_connection, 
        database, 
        llm_config=llm_config, 
        checkpointer=checkpointer
    )

    console.print(Panel(
        "[bold]KAI Autonomous Agent[/bold]\n"
        "Type your questions, 'exit' to quit, 'help' for commands",
        title="Interactive Mode"
    ))

    # Persistent thread ID for the session
    session_id = f"interactive_{uuid.uuid4().hex[:8]}"

    while True:
        try:
            prompt = console.input("\n[bold cyan]kai>[/bold cyan] ").strip()

            if not prompt:
                continue
            if prompt.lower() == "exit":
                break
            if prompt.lower() == "help":
                console.print("Commands: exit, help, clear")
                continue
            if prompt.lower() == "clear":
                console.clear()
                continue

            task = AgentTask(
                id=session_id,
                prompt=prompt,
                db_connection_id=db_connection_id,
            )

            await _render_stream(service, task, console)

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit[/dim]")
        except EOFError:
            break

    console.print("\n[dim]Session ended[/dim]")


@cli.command()
@click.argument("session_id")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
def debug_memory(session_id: str, db_connection_id: str):
    """Debug memory injection for a session.

    Shows what memory would be injected when resuming a session.

    Example:
        kai-agent debug-memory calm-river-472 --db conn_123
    """
    from app.server.config import Settings
    from app.modules.autonomous_agent.learning import get_agent_name, get_memory_blocks

    settings = Settings()

    if not settings.ENABLE_AUTO_LEARNING:
        console.print("[yellow]Auto-learning is disabled (ENABLE_AUTO_LEARNING=False)[/yellow]")
        return

    if not settings.LETTA_API_KEY:
        console.print("[red]LETTA_API_KEY not set[/red]")
        return

    try:
        from agentic_learning import AgenticLearning

        client = AgenticLearning(
            api_key=settings.LETTA_API_KEY,
            base_url=settings.LETTA_BASE_URL,
        )

        agent_name = get_agent_name(db_connection_id, session_id)
        memory_blocks = get_memory_blocks()

        console.print(f"[bold]Session Debug Info[/bold]")
        console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
        console.print(f"  DB Connection: [cyan]{db_connection_id}[/cyan]")
        console.print(f"  Agent Name: [cyan]{agent_name}[/cyan]")
        console.print(f"  Memory Blocks: [cyan]{memory_blocks}[/cyan]")
        console.print()

        # Check if agent exists
        agent = client.agents.retrieve(agent=agent_name)
        if not agent:
            console.print("[yellow]Agent does not exist yet.[/yellow]")
            console.print("[dim]It will be created on first use.[/dim]")
            return

        console.print(f"[green]✔ Agent exists[/green]")
        console.print(f"  Agent ID: {agent.id}")
        console.print()

        # List memory blocks
        console.print("[bold]Memory Blocks:[/bold]")
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'blocks'):
            for block in agent.memory.blocks:
                value_preview = block.value[:100] + "..." if block.value and len(block.value) > 100 else (block.value or "(empty)")
                console.print(f"  [{block.label}]")
                console.print(f"    {value_preview}")
        else:
            console.print("  [dim]No blocks found[/dim]")

        console.print()

        # Get memory context (what gets injected)
        console.print("[bold]Memory Context (injected into prompts):[/bold]")
        context = client.memory.context.retrieve(agent=agent_name)
        if context:
            console.print(context)
        else:
            console.print("[dim]No memory context to inject[/dim]")

    except ImportError:
        console.print("[red]agentic-learning not installed[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


    # Confirm unless forced
    if not force:
        console.print(f"[yellow]About to delete connection:[/yellow]")
        console.print(f"  ID: {conn.id}")
        console.print(f"  Alias: {conn.alias}")
        console.print(f"  Dialect: {conn.dialect}")
        if not click.confirm("\nDo you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        deleted = service.delete_database_connection(conn.id)
        console.print(Panel(
            f"[bold green]✔ Connection deleted[/bold green]\n\n"
            f"[cyan]Alias:[/cyan] {deleted.alias}\n"
            f"[cyan]ID:[/cyan] {deleted.id}",
            title="Connection Deleted",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]Error deleting connection:[/red] {e}")
        raise click.Abort()

@cli.command()
@click.argument("db_connection_id")
def show_connection(db_connection_id: str):
    """Show details of a database connection.

    Example:

        kai-agent show-connection abc123
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
        f"[bold]ID:[/bold] {db_connection.id}\n"
        f"[bold]Alias:[/bold] {db_connection.alias}\n"
        f"[bold]Dialect:[/bold] {db_connection.dialect}\n"
        f"[bold]Connection:[/bold] {safe_uri}\n"
        f"[bold]Schemas:[/bold] {', '.join(db_connection.schemas)}\n"
        f"[bold]Created:[/bold] {db_connection.created_at}\n"
        f"[bold]Description:[/bold] {db_connection.description or 'N/A'}",
        title=f"Connection: {db_connection.alias}",
        border_style="cyan"
    ))

    if tables:
        console.print(f"\n[bold]Associated Tables ({len(tables)}):[/bold]")
        for table in tables[:20]:
            status_color = "green" if table.sync_status == "SCANNED" else "yellow"
            console.print(f"  [{status_color}]●[/{status_color}] {table.db_schema}.{table.table_name} ({table.sync_status})")
        if len(tables) > 20:
            console.print(f"  [dim]... and {len(tables) - 20} more[/dim]")


@cli.command()
@click.argument("db_connection_id")
@click.option("--alias", "-a", help="New alias for the connection")
@click.option("--schema", "-s", "schemas", multiple=True, help="New schema(s) to use (replaces existing)")
@click.option("--metadata", "-m", type=str, help="JSON metadata for the connection")
@click.option("--uri", "-u", "connection_uri", help="New connection URI")
def update_connection(db_connection_id: str, alias: str, schemas: tuple, metadata: str, connection_uri: str):
    """Update an existing database connection.

    Examples:

        kai-agent update-connection abc123 --alias new_name

        kai-agent update-connection abc123 -s public -s analytics

        kai-agent update-connection abc123 --uri "postgresql://user:pass@newhost:5432/db"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import DatabaseConnectionRequest
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.utils.sql_database.scanner import SqlAlchemyScanner
    from app.utils.core.encrypt import FernetEncrypt

    settings = Settings()
    storage = Storage(settings)
    scanner = SqlAlchemyScanner()
    service = DatabaseConnectionService(scanner, storage)
    db_repo = DatabaseConnectionRepository(storage)

    # Get existing connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Parse metadata if provided
    meta_dict = db_connection.metadata
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Use existing values if not provided
    fernet = FernetEncrypt()
    existing_uri = fernet.decrypt(db_connection.connection_uri) if not connection_uri else connection_uri

    request = DatabaseConnectionRequest(
        alias=alias or db_connection.alias,
        connection_uri=existing_uri,
        schemas=list(schemas) if schemas else db_connection.schemas,
        metadata=meta_dict,
    )

    console.print(f"[bold]Updating connection '{db_connection.alias}'...[/bold]")

    try:
        with console.status("[bold cyan]Updating connection and rescanning tables...[/bold cyan]"):
            updated_connection = service.update_database_connection(db_connection_id, request)

        console.print(f"\n[green]✔ Connection updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated_connection.id}\n"
            f"[bold]Alias:[/bold] {updated_connection.alias}\n"
            f"[bold]Dialect:[/bold] {updated_connection.dialect}\n"
            f"[bold]Schemas:[/bold] {', '.join(updated_connection.schemas)}",
            title="Updated Connection",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to update connection:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--table", "-t", "table_ids", multiple=True, help="Specific table ID(s) to scan (scans all if not specified)")
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
        kai-agent scan-tables abc123

        # Scan specific tables
        kai-agent scan-tables abc123 -t table_id_1 -t table_id_2

        # Scan with AI-generated descriptions
        kai-agent scan-tables abc123 --with-descriptions

        # Use specific LLM for descriptions
        kai-agent scan-tables abc123 -d --model-family openai --model-name gpt-4o
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.modules.sql_generation.models import LLMConfig
    from app.utils.sql_database.scanner import SqlAlchemyScanner

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


@cli.command()
@click.argument("db_connection_id")
def refresh_tables(db_connection_id: str):
    """Refresh the table list from database.

    This command syncs the table list with the actual database,
    adding new tables and marking removed ones as deprecated.

    Example:

        kai-agent refresh-tables abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.table_description.services import TableDescriptionService

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


@cli.command()
@click.argument("db_connection_id")
@click.option("--schema", "-s", help="Filter by schema")
@click.option("--status", type=click.Choice(["all", "scanned", "not_scanned", "failed"]), default="all", help="Filter by scan status")
@click.option("--verbose", "-v", is_flag=True, help="Show full descriptions and column counts")
@click.option("--columns", "-c", is_flag=True, help="Show column names for each table")
def list_tables(db_connection_id: str, schema: str, status: str, verbose: bool, columns: bool):
    """List tables for a database connection.

    Examples:

        kai-agent list-tables abc123

        kai-agent list-tables abc123 --schema public

        kai-agent list-tables abc123 --status not_scanned

        kai-agent list-tables abc123 --verbose

        kai-agent list-tables abc123 --columns
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository

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


@cli.command()
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
        kai-agent scan-all abc123

        # Scan all with AI descriptions
        kai-agent scan-all abc123 --with-descriptions

        # Skip refresh, just scan existing tables
        kai-agent scan-all abc123 --no-refresh

        # Use OpenAI for descriptions
        kai-agent scan-all abc123 -d --model-family openai --model-name gpt-4o

        # Generate MDL semantic layer after scan
        kai-agent scan-all abc123 --generate-mdl

        # Generate MDL with custom name
        kai-agent scan-all abc123 -m --mdl-name "Sales Analytics"

        # Full scan with descriptions and MDL generation
        kai-agent scan-all abc123 -d -m --mdl-name "E-Commerce Semantic Layer"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.modules.table_description.repositories import TableDescriptionRepository
    from app.modules.table_description.services import TableDescriptionService
    from app.modules.sql_generation.models import LLMConfig
    from app.utils.sql_database.scanner import SqlAlchemyScanner

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
                import asyncio
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
                    manifest_id = asyncio.get_event_loop().run_until_complete(
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
                manifest = asyncio.get_event_loop().run_until_complete(
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


@cli.command()
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
        kai-agent db-context abc123

        # Include sample data
        kai-agent db-context abc123 --include-samples

        # Include DDL statements
        kai-agent db-context abc123 --include-ddl

        # Export as markdown
        kai-agent db-context abc123 -f markdown -o context.md

        # Export as JSON
        kai-agent db-context abc123 -f json -o context.json

        # Full context with everything
        kai-agent db-context abc123 -s -d -f markdown -o full_context.md
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

    # Get connection
    db_connection = db_repo.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    # Get all tables
    tables = table_repo.find_by({"db_connection_id": db_connection_id})

    if not tables:
        console.print("[yellow]No tables found. Run 'kai-agent scan-all' first.[/yellow]")
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


@cli.command()
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
        kai-agent search-tables abc123 "kpi"

        # Search for columns ending with '_id'
        kai-agent search-tables abc123 "*_id"

        # Search for tables starting with 'dim_'
        kai-agent search-tables abc123 "dim_*" --search-in tables

        # Search only in descriptions
        kai-agent search-tables abc123 "revenue" -i descriptions

        # Case-sensitive search
        kai-agent search-tables abc123 "KPI" --case-sensitive

        # Output as JSON
        kai-agent search-tables abc123 "*order*" -f json
    """
    import re
    import fnmatch
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.table_description.repositories import TableDescriptionRepository

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
        console.print("[yellow]No tables found. Run 'kai-agent scan-all' first.[/yellow]")
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


@cli.command()
@click.argument("table_id")
def show_table(table_id: str):
    """Show detailed information about a table.

    Example:

        kai-agent show-table table_abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.table_description.repositories import TableDescriptionRepository

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


@cli.command()
@click.argument("db_connection_id")
@click.option("--metric", "-m", required=True, help="Business metric name (e.g., 'Revenue', 'MRR', 'Churn Rate')")
@click.option("--sql", "-s", required=True, help="SQL query that calculates this metric")
@click.option("--alias", "-a", "aliases", multiple=True, help="Alternative names for this metric (can specify multiple)")
@click.option("--metadata", type=str, help="JSON metadata for the glossary entry")
def add_glossary(db_connection_id: str, metric: str, sql: str, aliases: tuple, metadata: str):
    """Add a new business glossary entry.

    Business glossary entries define business metrics and their SQL calculations.
    The agent uses these to understand business terminology when answering questions.

    Examples:

        # Simple metric
        kai-agent add-glossary abc123 --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"

        # Metric with aliases
        kai-agent add-glossary abc123 -m "MRR" -s "SELECT SUM(amount) FROM subscriptions WHERE status='active'" -a "Monthly Recurring Revenue" -a "Recurring Revenue"

        # Metric with metadata
        kai-agent add-glossary abc123 -m "Churn Rate" -s "SELECT COUNT(*) FILTER (WHERE churned) * 100.0 / COUNT(*) FROM customers" --metadata '{"unit": "percentage", "category": "retention"}'
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import BusinessGlossaryRequest
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    request = BusinessGlossaryRequest(
        metric=metric,
        alias=list(aliases) if aliases else None,
        sql=sql,
        metadata=meta_dict,
    )

    console.print(f"[bold]Adding business glossary entry...[/bold]")
    console.print(f"[dim]Metric: {metric}[/dim]")
    console.print(f"[dim]SQL: {sql[:60]}...[/dim]" if len(sql) > 60 else f"[dim]SQL: {sql}[/dim]")

    try:
        glossary = service.create_business_glossary(db_connection_id, request)

        console.print(f"\n[green]✔ Glossary entry created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {glossary.id}\n"
            f"[bold]Metric:[/bold] {glossary.metric}\n"
            f"[bold]Aliases:[/bold] {', '.join(glossary.alias) if glossary.alias else 'None'}\n"
            f"[bold]SQL:[/bold] {glossary.sql}\n"
            f"[bold]Created:[/bold] {glossary.created_at}",
            title="Business Glossary Entry",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to create glossary entry:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--verbose", "-v", is_flag=True, help="Show full SQL queries")
def list_glossaries(db_connection_id: str, verbose: bool):
    """List all business glossary entries for a connection.

    Examples:

        kai-agent list-glossaries abc123

        kai-agent list-glossaries abc123 --verbose
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    glossaries = service.get_business_glossaries(db_connection_id)

    if not glossaries:
        console.print("[yellow]No business glossary entries found[/yellow]")
        console.print(f"[dim]Add one with: kai-agent add-glossary {db_connection_id} -m 'Metric Name' -s 'SELECT ...'[/dim]")
        return

    console.print(f"[bold]Business Glossary ({len(glossaries)} entries):[/bold]\n")

    for g in glossaries:
        console.print(f"  [cyan]●[/cyan] [bold]{g.metric}[/bold]")
        console.print(f"      [dim]ID: {g.id}[/dim]")

        if g.alias:
            console.print(f"      [italic]Aliases: {', '.join(g.alias)}[/italic]")

        if verbose:
            console.print(f"      [dim]SQL: {g.sql}[/dim]")
        else:
            sql_preview = g.sql[:60] + "..." if len(g.sql) > 60 else g.sql
            console.print(f"      [dim]SQL: {sql_preview}[/dim]")

        if g.metadata:
            console.print(f"      [dim]Metadata: {g.metadata}[/dim]")

        console.print()


@cli.command()
@click.argument("glossary_id")
def show_glossary(glossary_id: str):
    """Show details of a business glossary entry.

    Example:

        kai-agent show-glossary glossary_abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    try:
        glossary = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(Panel(
        f"[bold]ID:[/bold] {glossary.id}\n"
        f"[bold]Metric:[/bold] {glossary.metric}\n"
        f"[bold]Aliases:[/bold] {', '.join(glossary.alias) if glossary.alias else 'None'}\n"
        f"[bold]Connection ID:[/bold] {glossary.db_connection_id}\n"
        f"[bold]Created:[/bold] {glossary.created_at}\n"
        f"[bold]Metadata:[/bold] {glossary.metadata or 'None'}",
        title=f"Business Glossary: {glossary.metric}",
        border_style="cyan"
    ))

    console.print(f"\n[bold]SQL Definition:[/bold]")
    console.print(Panel(glossary.sql, border_style="dim"))


@cli.command()
@click.argument("glossary_id")
@click.option("--metric", "-m", help="New metric name")
@click.option("--sql", "-s", help="New SQL query")
@click.option("--alias", "-a", "aliases", multiple=True, help="New alias(es) - replaces existing")
@click.option("--metadata", type=str, help="New JSON metadata")
def update_glossary(glossary_id: str, metric: str, sql: str, aliases: tuple, metadata: str):
    """Update an existing business glossary entry.

    Examples:

        # Update SQL
        kai-agent update-glossary glossary_abc123 --sql "SELECT SUM(amount) FROM orders WHERE status='completed'"

        # Update metric name
        kai-agent update-glossary glossary_abc123 --metric "Total Revenue"

        # Update aliases
        kai-agent update-glossary glossary_abc123 -a "Gross Revenue" -a "Sales Revenue"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import UpdateBusinessGlossaryRequest
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Check if glossary exists
    try:
        existing = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Build update request with only provided fields
    update_data = {}
    if metric:
        update_data["metric"] = metric
    if sql:
        update_data["sql"] = sql
    if aliases:
        update_data["alias"] = list(aliases)
    if meta_dict is not None:
        update_data["metadata"] = meta_dict

    if not update_data:
        console.print("[yellow]No updates provided[/yellow]")
        return

    request = UpdateBusinessGlossaryRequest(**update_data)

    console.print(f"[bold]Updating glossary entry '{existing.metric}'...[/bold]")

    try:
        updated = service.update_business_glossary(glossary_id, request)

        console.print(f"\n[green]✔ Glossary entry updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated.id}\n"
            f"[bold]Metric:[/bold] {updated.metric}\n"
            f"[bold]Aliases:[/bold] {', '.join(updated.alias) if updated.alias else 'None'}\n"
            f"[bold]SQL:[/bold] {updated.sql}",
            title="Updated Glossary Entry",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to update glossary entry:[/red] {str(e)}")


@cli.command()
@click.argument("glossary_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_glossary(glossary_id: str, force: bool):
    """Delete a business glossary entry.

    Examples:

        kai-agent delete-glossary glossary_abc123

        kai-agent delete-glossary glossary_abc123 --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Check if glossary exists
    try:
        glossary = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(f"[bold]Glossary entry to delete:[/bold]")
    console.print(f"  ID: {glossary.id}")
    console.print(f"  Metric: {glossary.metric}")
    console.print(f"  SQL: {glossary.sql[:60]}..." if len(glossary.sql) > 60 else f"  SQL: {glossary.sql}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this glossary entry?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_business_glossary(glossary_id)
        console.print(f"\n[green]✔ Glossary entry '{glossary.metric}' deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete glossary entry:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--condition", "-c", required=True, help="When this instruction applies (e.g., 'When asked about revenue')")
@click.option("--rules", "-r", required=True, help="The rules/guidelines to follow")
@click.option("--default", "-d", "is_default", is_flag=True, help="Make this instruction always apply (default instructions)")
@click.option("--metadata", type=str, help="JSON metadata for the instruction")
def add_instruction(db_connection_id: str, condition: str, rules: str, is_default: bool, metadata: str):
    """Add a custom instruction for the AI agent.

    Instructions customize how the agent responds to certain types of questions.
    - Default instructions always apply to every query
    - Non-default instructions are retrieved based on semantic relevance

    Examples:

        # Add a default instruction (always applies)
        kai-agent add-instruction abc123 -c "Always" -r "Format currency values with $ symbol" --default

        # Add a conditional instruction (retrieved when relevant)
        kai-agent add-instruction abc123 -c "When asked about revenue" -r "Use the revenue_by_month view, not raw transactions"

        # Add instruction with metadata
        kai-agent add-instruction abc123 -c "When calculating churn" -r "Exclude trial users from churn calculations" --metadata '{"category": "metrics"}'
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import InstructionRequest
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    request = InstructionRequest(
        db_connection_id=db_connection_id,
        condition=condition,
        rules=rules,
        is_default=is_default,
        metadata=meta_dict,
    )

    console.print(f"[bold]Adding instruction...[/bold]")
    console.print(f"[dim]Condition: {condition}[/dim]")
    console.print(f"[dim]Type: {'Default (always applies)' if is_default else 'Conditional (semantic search)'}[/dim]")

    try:
        instruction = service.create_instruction(request)

        console.print(f"\n[green]✔ Instruction created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {instruction.id}\n"
            f"[bold]Condition:[/bold] {instruction.condition}\n"
            f"[bold]Rules:[/bold] {instruction.rules}\n"
            f"[bold]Default:[/bold] {'Yes' if instruction.is_default else 'No'}\n"
            f"[bold]Created:[/bold] {instruction.created_at}",
            title="Instruction",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to create instruction:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--type", "-t", "filter_type", type=click.Choice(["all", "default", "conditional"]), default="all", help="Filter by instruction type")
@click.option("--verbose", "-v", is_flag=True, help="Show full rules text")
def list_instructions(db_connection_id: str, filter_type: str, verbose: bool):
    """List all instructions for a database connection.

    Examples:

        kai-agent list-instructions abc123

        kai-agent list-instructions abc123 --type default

        kai-agent list-instructions abc123 --verbose
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    instructions = service.get_instructions(db_connection_id)

    # Filter by type
    if filter_type == "default":
        instructions = [i for i in instructions if i.is_default]
    elif filter_type == "conditional":
        instructions = [i for i in instructions if not i.is_default]

    if not instructions:
        console.print("[yellow]No instructions found[/yellow]")
        console.print(f"[dim]Add one with: kai-agent add-instruction {db_connection_id} -c 'Condition' -r 'Rules'[/dim]")
        return

    # Separate default and conditional
    default_instructions = [i for i in instructions if i.is_default]
    conditional_instructions = [i for i in instructions if not i.is_default]

    console.print(f"[bold]Instructions ({len(instructions)} total):[/bold]\n")

    if default_instructions:
        console.print(f"[cyan]Default Instructions ({len(default_instructions)}):[/cyan]")
        console.print("[dim]These always apply to every query[/dim]\n")
        for inst in default_instructions:
            console.print(f"  [green]●[/green] [bold]{inst.condition}[/bold]")
            console.print(f"      [dim]ID: {inst.id}[/dim]")
            if verbose:
                console.print(f"      [italic]Rules: {inst.rules}[/italic]")
            else:
                rules_preview = inst.rules[:80] + "..." if len(inst.rules) > 80 else inst.rules
                console.print(f"      [italic]Rules: {rules_preview}[/italic]")
            console.print()

    if conditional_instructions:
        console.print(f"[cyan]Conditional Instructions ({len(conditional_instructions)}):[/cyan]")
        console.print("[dim]These are retrieved based on semantic relevance[/dim]\n")
        for inst in conditional_instructions:
            console.print(f"  [yellow]●[/yellow] [bold]{inst.condition}[/bold]")
            console.print(f"      [dim]ID: {inst.id}[/dim]")
            if verbose:
                console.print(f"      [italic]Rules: {inst.rules}[/italic]")
            else:
                rules_preview = inst.rules[:80] + "..." if len(inst.rules) > 80 else inst.rules
                console.print(f"      [italic]Rules: {rules_preview}[/italic]")
            console.print()


@cli.command()
@click.argument("instruction_id")
def show_instruction(instruction_id: str):
    """Show details of an instruction.

    Example:

        kai-agent show-instruction instruction_abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    try:
        instruction = service.get_instruction(instruction_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    type_label = "[green]DEFAULT[/green] (always applies)" if instruction.is_default else "[yellow]CONDITIONAL[/yellow] (semantic search)"

    console.print(Panel(
        f"[bold]ID:[/bold] {instruction.id}\n"
        f"[bold]Connection ID:[/bold] {instruction.db_connection_id}\n"
        f"[bold]Type:[/bold] {type_label}\n"
        f"[bold]Created:[/bold] {instruction.created_at}\n"
        f"[bold]Metadata:[/bold] {instruction.metadata or 'None'}",
        title=f"Instruction: {instruction.condition[:50]}...",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Condition (When):[/bold]")
    console.print(Panel(instruction.condition, border_style="dim"))

    console.print(f"\n[bold]Rules (What to do):[/bold]")
    console.print(Panel(instruction.rules, border_style="dim"))


@cli.command()
@click.argument("instruction_id")
@click.option("--condition", "-c", help="New condition")
@click.option("--rules", "-r", help="New rules")
@click.option("--default/--no-default", "is_default", default=None, help="Set as default or conditional")
@click.option("--metadata", type=str, help="New JSON metadata")
def update_instruction(instruction_id: str, condition: str, rules: str, is_default: bool, metadata: str):
    """Update an existing instruction.

    Examples:

        # Update rules
        kai-agent update-instruction instruction_abc123 --rules "New rules text"

        # Update condition
        kai-agent update-instruction instruction_abc123 --condition "New condition"

        # Make it a default instruction
        kai-agent update-instruction instruction_abc123 --default

        # Make it conditional (non-default)
        kai-agent update-instruction instruction_abc123 --no-default
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import UpdateInstructionRequest
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Check if instruction exists
    try:
        service.get_instruction(instruction_id)  # Raises if not found
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Build update request with only provided fields
    update_data = {}
    if condition:
        update_data["condition"] = condition
    if rules:
        update_data["rules"] = rules
    if is_default is not None:
        update_data["is_default"] = is_default
    if meta_dict is not None:
        update_data["metadata"] = meta_dict

    if not update_data:
        console.print("[yellow]No updates provided[/yellow]")
        return

    request = UpdateInstructionRequest(**update_data)

    console.print(f"[bold]Updating instruction...[/bold]")

    try:
        updated = service.update_instruction(instruction_id, request)

        console.print(f"\n[green]✔ Instruction updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated.id}\n"
            f"[bold]Condition:[/bold] {updated.condition}\n"
            f"[bold]Rules:[/bold] {updated.rules}\n"
            f"[bold]Default:[/bold] {'Yes' if updated.is_default else 'No'}",
            title="Updated Instruction",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to update instruction:[/red] {str(e)}")


@cli.command()
@click.argument("instruction_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_instruction(instruction_id: str, force: bool):
    """Delete an instruction.

    Examples:

        kai-agent delete-instruction instruction_abc123

        kai-agent delete-instruction instruction_abc123 --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Check if instruction exists
    try:
        instruction = service.get_instruction(instruction_id)
    except Exception as e:
        # Handle HTTPException with detail attribute
        error_msg = getattr(e, 'detail', str(e))
        console.print(f"[red]Error:[/red] {error_msg}")
        return

    console.print(f"[bold]Instruction to delete:[/bold]")
    console.print(f"  ID: {instruction.id}")
    console.print(f"  Condition: {instruction.condition}")
    console.print(f"  Type: {'Default' if instruction.is_default else 'Conditional'}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this instruction?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_instruction(instruction_id)
        console.print(f"\n[green]✔ Instruction deleted successfully![/green]")

    except Exception as e:
        # Handle HTTPException with detail attribute
        error_msg = getattr(e, 'detail', str(e))
        console.print(f"\n[red]✖ Failed to delete instruction:[/red] {error_msg}")


# ============================================================
# Skills Management Commands
# ============================================================


@cli.command()
@click.argument("db_connection_id")
@click.option("--path", "-p", default="./.skills", help="Path to skills directory")
@click.option("--sync/--no-sync", "sync_to_storage", default=True, help="Sync discovered skills to storage")
def discover_skills(db_connection_id: str, path: str, sync_to_storage: bool):
    """Discover and sync skills from a directory.

    Scans the specified directory (default: ./.skills) for SKILL.md files
    and syncs them to TypeSense storage.

    Examples:

        # Discover skills from default path
        kai-agent discover-skills abc123

        # Discover from custom path
        kai-agent discover-skills abc123 --path /path/to/skills

        # Preview without syncing
        kai-agent discover-skills abc123 --no-sync
    """
    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    skills_path = Path(path)
    console.print(f"[bold]Discovering skills in:[/bold] {skills_path.absolute()}")
    console.print(f"[dim]Sync to storage: {'Yes' if sync_to_storage else 'No (preview only)'}[/dim]")

    try:
        result = service.discover_skills(
            db_connection_id, skills_path, sync_to_storage=sync_to_storage
        )

        if result.total_found == 0:
            console.print("\n[yellow]No skills found[/yellow]")
            console.print(f"[dim]Expected SKILL.md files in subdirectories of {path}[/dim]")
            return

        console.print(f"\n[green]✔ Discovered {result.total_found} skill(s)[/green]")

        for skill in result.skills:
            status = "[green]active[/green]" if skill.is_active else "[dim]inactive[/dim]"
            console.print(f"  • [bold]{skill.skill_id}[/bold] ({skill.name}) {status}")
            console.print(f"    [dim]{skill.description}[/dim]")

        if result.total_errors > 0:
            console.print(f"\n[yellow]⚠ {result.total_errors} error(s):[/yellow]")
            for error in result.errors:
                console.print(f"  [red]✖[/red] {error}")

    except Exception as e:
        console.print(f"\n[red]✖ Discovery failed:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--active-only", "-a", is_flag=True, help="Show only active skills")
@click.option("--category", "-c", help="Filter by category")
def list_skills(db_connection_id: str, active_only: bool, category: str):
    """List all skills for a database connection.

    Examples:

        kai-agent list-skills abc123

        kai-agent list-skills abc123 --active-only

        kai-agent list-skills abc123 --category analysis
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    if active_only:
        skills = service.get_active_skills(db_connection_id)
    else:
        skills = service.get_skills(db_connection_id)

    # Filter by category if specified
    if category:
        skills = [s for s in skills if s.category == category]

    if not skills:
        console.print("[yellow]No skills found[/yellow]")
        console.print(f"[dim]Discover skills with: kai-agent discover-skills {db_connection_id}[/dim]")
        return

    console.print(f"[bold]Skills ({len(skills)} total):[/bold]\n")

    # Group by category
    by_category: dict = {}
    for skill in skills:
        cat = skill.category or "uncategorized"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for cat, cat_skills in sorted(by_category.items()):
        console.print(f"[cyan]{cat.upper()}[/cyan]")
        for skill in cat_skills:
            status = "[green]●[/green]" if skill.is_active else "[dim]○[/dim]"
            tags_str = f" [dim]({', '.join(skill.tags)})[/dim]" if skill.tags else ""
            console.print(f"  {status} [bold]{skill.skill_id}[/bold]: {skill.name}{tags_str}")
            desc = skill.description[:80] + "..." if len(skill.description) > 80 else skill.description
            console.print(f"      [dim]{desc}[/dim]")
        console.print()


@cli.command()
@click.argument("db_connection_id")
@click.argument("skill_id")
@click.option("--content", "-c", is_flag=True, help="Show full content")
def show_skill(db_connection_id: str, skill_id: str, content: bool):
    """Show details of a specific skill.

    Examples:

        kai-agent show-skill abc123 analysis/revenue

        kai-agent show-skill abc123 data-quality --content
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    try:
        skill = service.get_skill_by_skill_id(db_connection_id, skill_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    status = "[green]ACTIVE[/green]" if skill.is_active else "[dim]INACTIVE[/dim]"
    tags_str = ", ".join(skill.tags) if skill.tags else "None"

    console.print(Panel(
        f"[bold]Skill ID:[/bold] {skill.skill_id}\n"
        f"[bold]Name:[/bold] {skill.name}\n"
        f"[bold]Status:[/bold] {status}\n"
        f"[bold]Category:[/bold] {skill.category or 'None'}\n"
        f"[bold]Tags:[/bold] {tags_str}\n"
        f"[bold]File:[/bold] {skill.file_path}\n"
        f"[bold]Created:[/bold] {skill.created_at}\n"
        f"[bold]Updated:[/bold] {skill.updated_at}",
        title=f"Skill: {skill.name}",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Description:[/bold]")
    console.print(Panel(skill.description, border_style="dim"))

    if content:
        console.print(f"\n[bold]Content:[/bold]")
        console.print(Panel(skill.content, border_style="dim"))
    else:
        preview = skill.content[:500] + "..." if len(skill.content) > 500 else skill.content
        console.print(f"\n[bold]Content Preview:[/bold]")
        console.print(Panel(preview, border_style="dim"))
        if len(skill.content) > 500:
            console.print(f"[dim]Use --content to see full content[/dim]")


@cli.command()
@click.argument("db_connection_id")
@click.argument("query")
@click.option("--limit", "-l", default=5, help="Maximum number of results")
def search_skills(db_connection_id: str, query: str, limit: int):
    """Search for skills by keyword or description.

    Uses semantic search to find relevant skills.

    Examples:

        kai-agent search-skills abc123 "revenue analysis"

        kai-agent search-skills abc123 "data quality" --limit 10
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    console.print(f"[bold]Searching for:[/bold] {query}")

    try:
        skills = service.find_relevant_skills(db_connection_id, query, limit=limit)

        if not skills:
            console.print("\n[yellow]No skills found matching your query[/yellow]")
            console.print("[dim]Try different keywords or use list-skills to see all available[/dim]")
            return

        console.print(f"\n[green]Found {len(skills)} skill(s):[/green]\n")

        for i, skill in enumerate(skills, 1):
            status = "[green]●[/green]" if skill.is_active else "[dim]○[/dim]"
            console.print(f"{i}. {status} [bold]{skill.skill_id}[/bold]: {skill.name}")
            console.print(f"   [dim]{skill.description}[/dim]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.argument("skill_id")
@click.option("--path", "-p", default="./.skills", help="Path to skills directory")
def reload_skill(db_connection_id: str, skill_id: str, path: str):
    """Reload a skill from its file.

    Use this after modifying a SKILL.md file to sync changes to storage.

    Examples:

        kai-agent reload-skill abc123 analysis/revenue

        kai-agent reload-skill abc123 data-quality --path /custom/path
    """
    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    skills_path = Path(path)
    console.print(f"[bold]Reloading skill:[/bold] {skill_id}")
    console.print(f"[dim]From: {skills_path.absolute()}/{skill_id}/SKILL.md[/dim]")

    try:
        skill = service.reload_skill_from_file(db_connection_id, skill_id, skills_path)

        console.print(f"\n[green]✔ Skill reloaded successfully![/green]")
        console.print(Panel(
            f"[bold]Skill ID:[/bold] {skill.skill_id}\n"
            f"[bold]Name:[/bold] {skill.name}\n"
            f"[bold]Description:[/bold] {skill.description}\n"
            f"[bold]Updated:[/bold] {skill.updated_at}",
            title="Reloaded Skill",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to reload skill:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.argument("skill_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_skill(db_connection_id: str, skill_id: str, force: bool):
    """Delete a skill from storage.

    This removes the skill from TypeSense storage. The SKILL.md file is not deleted.

    Examples:

        kai-agent delete-skill abc123 analysis/revenue

        kai-agent delete-skill abc123 data-quality --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    try:
        skill = service.get_skill_by_skill_id(db_connection_id, skill_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(f"[bold]Skill to delete:[/bold]")
    console.print(f"  ID: {skill.skill_id}")
    console.print(f"  Name: {skill.name}")
    console.print(f"  Category: {skill.category or 'None'}")

    if not force:
        console.print("\n[dim]Note: This only removes the skill from storage.")
        console.print("The SKILL.md file will not be deleted.[/dim]")
        if not click.confirm("\nAre you sure you want to delete this skill?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_skill(db_connection_id, skill_id)
        console.print(f"\n[green]✔ Skill deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete skill:[/red] {str(e)}")


# =============================================================================
# Memory Commands
# =============================================================================


@cli.command()
@click.argument("db_connection_id")
@click.option("--namespace", "-n", help="Filter by namespace")
@click.option("--limit", "-l", default=50, help="Maximum number of memories to show")
def list_memories(db_connection_id: str, namespace: str, limit: int):
    """List all memories for a database connection.

    Examples:

        kai-agent list-memories abc123

        kai-agent list-memories abc123 --namespace user_preferences

        kai-agent list-memories abc123 -n business_facts --limit 20
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    memories = service.list_memories(db_connection_id, namespace=namespace, limit=limit)

    if not memories:
        console.print("[yellow]No memories found[/yellow]")
        console.print("[dim]Memories are created when the agent stores insights from conversations.[/dim]")
        return

    console.print(f"[bold]Memories ({len(memories)} total):[/bold]\n")

    # Group by namespace
    by_namespace: dict = {}
    for memory in memories:
        ns = memory.namespace
        if ns not in by_namespace:
            by_namespace[ns] = []
        by_namespace[ns].append(memory)

    for ns, ns_memories in sorted(by_namespace.items()):
        console.print(f"[cyan]{ns.upper()}[/cyan]")
        for memory in ns_memories:
            importance_color = "green" if memory.importance >= 0.7 else "yellow" if memory.importance >= 0.4 else "dim"
            console.print(f"  • [bold]{memory.key}[/bold] [{importance_color}]{memory.importance:.1f}[/{importance_color}]")
            content = memory.value.get("content", str(memory.value))
            content_preview = content[:100] + "..." if len(content) > 100 else content
            console.print(f"    [dim]{content_preview}[/dim]")
            console.print(f"    [dim]Accessed: {memory.access_count}x | Created: {memory.created_at}[/dim]")
        console.print()


@cli.command()
@click.argument("db_connection_id")
@click.argument("namespace")
@click.argument("key")
def show_memory(db_connection_id: str, namespace: str, key: str):
    """Show details of a specific memory.

    Examples:

        kai-agent show-memory abc123 user_preferences date_format

        kai-agent show-memory abc123 business_facts q4_revenue_rule
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    memory = service.get_memory(db_connection_id, namespace, key)

    if not memory:
        console.print(f"[red]Memory not found:[/red] {namespace}/{key}")
        return

    importance_color = "green" if memory.importance >= 0.7 else "yellow" if memory.importance >= 0.4 else "white"

    console.print(Panel(
        f"[bold]Namespace:[/bold] {memory.namespace}\n"
        f"[bold]Key:[/bold] {memory.key}\n"
        f"[bold]Importance:[/bold] [{importance_color}]{memory.importance}[/{importance_color}]\n"
        f"[bold]Access Count:[/bold] {memory.access_count}\n"
        f"[bold]Last Accessed:[/bold] {memory.last_accessed_at or 'Never'}\n"
        f"[bold]Created:[/bold] {memory.created_at}\n"
        f"[bold]Updated:[/bold] {memory.updated_at}",
        title=f"Memory: {namespace}/{key}",
        border_style="cyan"
    ))

    content = memory.value.get("content", str(memory.value))
    console.print(f"\n[bold]Content:[/bold]")
    console.print(Panel(content, border_style="dim"))


@cli.command()
@click.argument("db_connection_id")
@click.argument("query")
@click.option("--namespace", "-n", help="Search within a specific namespace")
@click.option("--limit", "-l", default=10, help="Maximum number of results")
def search_memories(db_connection_id: str, query: str, namespace: str, limit: int):
    """Search memories semantically.

    Uses semantic search to find relevant memories.

    Examples:

        kai-agent search-memories abc123 "date format preferences"

        kai-agent search-memories abc123 "revenue" --namespace business_facts

        kai-agent search-memories abc123 "data issues" --limit 5
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    console.print(f"[bold]Searching memories for:[/bold] {query}")

    results = service.recall(db_connection_id, query, namespace=namespace, limit=limit)

    if not results:
        console.print("\n[yellow]No memories found matching your query[/yellow]")
        return

    console.print(f"\n[green]Found {len(results)} memory(ies):[/green]\n")

    for i, result in enumerate(results, 1):
        memory = result.memory
        score_color = "green" if result.score >= 0.7 else "yellow" if result.score >= 0.4 else "dim"
        console.print(f"{i}. [bold]{memory.namespace}/{memory.key}[/bold] [{score_color}]score: {result.score:.2f}[/{score_color}]")
        content = memory.value.get("content", str(memory.value))
        content_preview = content[:150] + "..." if len(content) > 150 else content
        console.print(f"   [dim]{content_preview}[/dim]")
        console.print()


@cli.command()
@click.argument("db_connection_id")
@click.argument("namespace")
@click.argument("key")
@click.argument("content")
@click.option("--importance", "-i", default=0.5, type=float, help="Importance (0-1)")
def add_memory(db_connection_id: str, namespace: str, key: str, content: str, importance: float):
    """Manually add a memory.

    Useful for pre-populating important facts or preferences.

    Examples:

        kai-agent add-memory abc123 user_preferences date_format "Use YYYY-MM-DD format"

        kai-agent add-memory abc123 business_facts fiscal_year "Fiscal year ends in June" -i 0.9

        kai-agent add-memory abc123 corrections revenue_calc "Revenue should exclude refunds" -i 0.8
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    if importance < 0 or importance > 1:
        console.print("[red]Error:[/red] Importance must be between 0 and 1")
        return

    try:
        memory = service.remember(
            db_connection_id=db_connection_id,
            namespace=namespace,
            key=key,
            value={"content": content},
            importance=importance,
        )

        console.print(f"\n[green]✔ Memory stored successfully![/green]")
        console.print(Panel(
            f"[bold]Namespace:[/bold] {memory.namespace}\n"
            f"[bold]Key:[/bold] {memory.key}\n"
            f"[bold]Importance:[/bold] {memory.importance}\n"
            f"[bold]Content:[/bold] {content}",
            title="New Memory",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to store memory:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.argument("namespace")
@click.argument("key")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_memory(db_connection_id: str, namespace: str, key: str, force: bool):
    """Delete a specific memory.

    Examples:

        kai-agent delete-memory abc123 user_preferences old_format

        kai-agent delete-memory abc123 business_facts outdated_rule --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    memory = service.get_memory(db_connection_id, namespace, key)

    if not memory:
        console.print(f"[red]Memory not found:[/red] {namespace}/{key}")
        return

    console.print(f"[bold]Memory to delete:[/bold]")
    console.print(f"  Namespace: {namespace}")
    console.print(f"  Key: {key}")
    content = memory.value.get("content", str(memory.value))
    content_preview = content[:100] + "..." if len(content) > 100 else content
    console.print(f"  Content: {content_preview}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this memory?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        success = service.forget(db_connection_id, namespace, key)
        if success:
            console.print(f"\n[green]✔ Memory deleted successfully![/green]")
        else:
            console.print(f"\n[red]✖ Failed to delete memory[/red]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete memory:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--namespace", "-n", help="Clear only this namespace")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def clear_memories(db_connection_id: str, namespace: str, force: bool):
    """Clear all memories for a database connection.

    Examples:

        kai-agent clear-memories abc123

        kai-agent clear-memories abc123 --namespace user_preferences

        kai-agent clear-memories abc123 --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    if namespace:
        console.print(f"[bold]Clearing memories in namespace:[/bold] {namespace}")
        memories = service.list_memories(db_connection_id, namespace=namespace)
    else:
        console.print(f"[bold]Clearing ALL memories for connection:[/bold] {db_connection_id}")
        memories = service.list_memories(db_connection_id)

    if not memories:
        console.print("[yellow]No memories to clear[/yellow]")
        return

    console.print(f"[yellow]This will delete {len(memories)} memory(ies)[/yellow]")

    if not force:
        if not click.confirm("\nAre you sure you want to delete these memories?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        if namespace:
            count = service.clear_namespace(db_connection_id, namespace)
        else:
            count = service.clear_all(db_connection_id)

        console.print(f"\n[green]✔ Cleared {count} memory(ies)[/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to clear memories:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
def list_namespaces(db_connection_id: str):
    """List all memory namespaces for a database connection.

    Examples:

        kai-agent list-namespaces abc123
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.memory.services import MemoryService

    settings = Settings()
    storage = Storage(settings)
    service = MemoryService(storage)

    namespaces = service.list_namespaces(db_connection_id)

    if not namespaces:
        console.print("[yellow]No namespaces found[/yellow]")
        console.print("[dim]Standard namespaces: user_preferences, business_facts, data_insights, corrections[/dim]")
        return

    console.print(f"[bold]Memory Namespaces:[/bold]\n")
    for ns in sorted(namespaces):
        memories = service.list_memories(db_connection_id, namespace=ns)
        console.print(f"  • [cyan]{ns}[/cyan] ({len(memories)} memories)")


@cli.command()
@click.option("--config", "config_path", help="Path to MCP servers config file")
def mcp_list(config_path: str | None):
    """List available MCP tools from configured servers.

    Examples:

        kai-agent mcp-list
        kai-agent mcp-list --config ./mcp-servers.json
    """
    from app.server.config import Settings

    settings = Settings()

    # Check if MCP is enabled
    mcp_enabled = getattr(settings, "MCP_ENABLED", False)
    path = config_path or getattr(settings, "MCP_SERVERS_CONFIG", None)

    if not mcp_enabled and not config_path:
        console.print("[yellow]MCP is not enabled[/yellow]")
        console.print("[dim]Set MCP_ENABLED=true and MCP_SERVERS_CONFIG in .env[/dim]")
        return

    if not path:
        console.print("[yellow]No MCP config specified[/yellow]")
        console.print("[dim]Set MCP_SERVERS_CONFIG in .env or use --config[/dim]")
        return

    try:
        from app.modules.mcp.client import MCPToolManager

        console.print(f"[dim]Loading MCP tools from: {path}[/dim]\n")

        manager = MCPToolManager(path)

        # Show configured servers
        servers = manager.list_servers()
        if servers:
            console.print("[bold]Configured MCP Servers:[/bold]")
            server_info = manager.get_server_info()
            for name in servers:
                info = server_info.get(name, {})
                transport = info.get("transport", "unknown")
                endpoint = info.get("url") or info.get("command") or ""
                console.print(f"  • [cyan]{name}[/cyan] ({transport}) {endpoint}")
            console.print()

        # Load and display tools
        tools = manager.get_tools_sync()

        if not tools:
            console.print("[yellow]No tools loaded from MCP servers[/yellow]")
            console.print("[dim]Check server configuration and connectivity[/dim]")
            return

        console.print(f"[bold]Available MCP Tools ({len(tools)}):[/bold]\n")
        for tool in tools:
            desc = tool.description[:70] + "..." if len(tool.description) > 70 else tool.description
            console.print(f"  • [cyan]{tool.name}[/cyan]")
            console.print(f"    {desc}")

    except ImportError:
        console.print("[red]langchain-mcp-adapters not installed[/red]")
        console.print("[dim]Install with: pip install langchain-mcp-adapters[/dim]")
    except FileNotFoundError:
        console.print(f"[red]Config file not found: {path}[/red]")
    except Exception as e:
        console.print(f"[red]Error loading MCP tools: {e}[/red]")


# =============================================================================
# Session Management Commands
# =============================================================================

@cli.command()
@click.option("--db", "db_connection_id", help="Filter by database connection ID")
@click.option("--status", type=click.Choice(["idle", "processing", "error", "closed"]), help="Filter by status")
@click.option("--limit", "-l", default=50, help="Maximum number of sessions to show")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed session info")
def list_sessions(db_connection_id: str | None, status: str | None, limit: int, verbose: bool):
    """List all conversation sessions.

    Examples:

        kai-agent list-sessions

        kai-agent list-sessions --db conn_123

        kai-agent list-sessions --status idle --limit 10

        kai-agent list-sessions -v  # Detailed view
    """
    asyncio.run(_list_sessions(db_connection_id, status, limit, verbose))


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


@cli.command()
@click.argument("session_id")
def show_session(session_id: str):
    """Show details of a specific session.

    Examples:

        kai-agent show-session sess_abc123

        kai-agent show-session brave-falcon-472
    """
    asyncio.run(_show_session(session_id))


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


@cli.command()
@click.argument("session_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_session(session_id: str, force: bool):
    """Delete a session.

    Examples:

        kai-agent delete-session sess_abc123

        kai-agent delete-session brave-falcon-472 -f
    """
    asyncio.run(_delete_session(session_id, force))


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


@cli.command()
@click.argument("session_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: session_<id>.json)")
@click.option("--format", "-f", "output_format", type=click.Choice(["json", "markdown"]), default="json", help="Export format")
def export_session(session_id: str, output: str | None, output_format: str):
    """Export a session to file.

    Examples:

        kai-agent export-session sess_abc123

        kai-agent export-session brave-falcon-472 -o my_session.json

        kai-agent export-session sess_abc123 -f markdown -o conversation.md
    """
    asyncio.run(_export_session(session_id, output, output_format))


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


@cli.command()
@click.option("--db", "db_connection_id", help="Filter by database connection ID")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def clear_sessions(db_connection_id: str | None, force: bool):
    """Clear all sessions (optionally for a specific database).

    Examples:

        kai-agent clear-sessions

        kai-agent clear-sessions --db conn_123

        kai-agent clear-sessions -f  # Skip confirmation
    """
    asyncio.run(_clear_sessions(db_connection_id, force))


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





# ============================================================================
# Dashboard Commands
# ============================================================================

@cli.command("create-dashboard")
@click.argument("request")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option("--name", help="Dashboard name (optional, auto-generated if not provided)")
@click.option("--theme", type=click.Choice(["default", "light", "dark", "ocean", "sunset", "forest"]), default="default", help="Dashboard theme")
def create_dashboard(request: str, db_connection_id: str, name: str | None, theme: str):
    """Create a dashboard from natural language.

    REQUEST: Natural language description of the dashboard

    Examples:

        kai-agent create-dashboard "Sales dashboard with revenue trends and top products" --db sales_db

        kai-agent create-dashboard "Customer analytics with churn metrics" --db crm --name "Customer 360"

        kai-agent create-dashboard "Executive KPI dashboard" --db prod --theme ocean
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService
    from app.modules.dashboard.models import CreateDashboardRequest

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    # Create request
    req = CreateDashboardRequest(
        request=request,
        db_connection_id=db_connection_id,
        name=name,
        theme=theme,
    )

    try:
        with console.status("[bold cyan]Creating dashboard...[/bold cyan]"):
            dashboard = asyncio.run(service.create_from_nl(req))

        console.print(Panel(
            f"[bold green]✔ Dashboard created successfully![/bold green]\n\n"
            f"[cyan]ID:[/cyan] {dashboard.id}\n"
            f"[cyan]Name:[/cyan] {dashboard.name}\n"
            f"[cyan]Widgets:[/cyan] {len(dashboard.layout.widgets)}\n"
            f"[cyan]Theme:[/cyan] {dashboard.theme}\n\n"
            f"[dim]View dashboard: http://localhost:8015/dashboards/{dashboard.id}[/dim]",
            title="Dashboard Created",
            border_style="green"
        ))

        # Show widgets
        console.print("\n[bold]Widgets:[/bold]")
        for widget in dashboard.layout.widgets:
            console.print(f"  • [cyan]{widget.type}[/cyan]: {widget.title or widget.name}")

    except Exception as e:
        console.print(f"[red]Error creating dashboard:[/red] {e}")
        raise click.Abort()


@cli.command("list-dashboards")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
def list_dashboards(db_connection_id: str):
    """List all dashboards for a database connection.

    Examples:

        kai-agent list-dashboards --db sales_db

        kai-agent list-dashboards --db prod
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    dashboards = service.list_by_connection(db_connection_id)

    if not dashboards:
        console.print("[yellow]No dashboards found[/yellow]")
        return

    from rich.table import Table

    table = Table(title=f"Dashboards for {db_connection_id}")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Widgets")
    table.add_column("Theme")
    table.add_column("Created")

    for dash in dashboards:
        table.add_row(
            dash.id[:20] + "..." if len(dash.id) > 20 else dash.id,
            dash.name,
            str(len(dash.layout.widgets)),
            dash.theme,
            dash.created_at.strftime("%Y-%m-%d") if hasattr(dash.created_at, 'strftime') else str(dash.created_at)[:10]
        )

    console.print(table)


@cli.command("show-dashboard")
@click.argument("dashboard_id")
def show_dashboard(dashboard_id: str):
    """Show detailed information about a dashboard.

    Examples:

        kai-agent show-dashboard abc123def456
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    dashboard = service.get(dashboard_id)

    if not dashboard:
        console.print(f"[red]Dashboard not found:[/red] {dashboard_id}")
        return

    from rich.table import Table

    console.print(Panel(
        f"[bold cyan]{dashboard.name}[/bold cyan]\n\n"
        f"[dim]{dashboard.description or 'No description'}[/dim]\n\n"
        f"[cyan]ID:[/cyan] {dashboard.id}\n"
        f"[cyan]Connection:[/cyan] {dashboard.db_connection_id}\n"
        f"[cyan]Widgets:[/cyan] {len(dashboard.layout.widgets)}\n"
        f"[cyan]Theme:[/cyan] {dashboard.theme}\n"
        f"[cyan]Layout:[/cyan] {dashboard.layout.columns} columns × {dashboard.layout.row_height} rows",
        title="Dashboard Details",
        border_style="cyan"
    ))

    # Show widgets table
    widget_table = Table(title="Widgets")
    widget_table.add_column("Type")
    widget_table.add_column("Title")
    widget_table.add_column("Position")
    widget_table.add_column("Size")

    for widget in dashboard.layout.widgets:
        widget_table.add_row(
            widget.type,
            widget.title or widget.name,
            f"({widget.x}, {widget.y})",
            f"{widget.width}×{widget.height}"
        )

    console.print(widget_table)


@cli.command("execute-dashboard")
@click.argument("dashboard_id")
def execute_dashboard(dashboard_id: str):
    """Execute all widgets in a dashboard (run queries).

    Examples:

        kai-agent execute-dashboard abc123def456
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    try:
        with console.status("[bold cyan]Executing dashboard...[/bold cyan]"):
            run = asyncio.run(service.execute(dashboard_id))

        console.print(f"[green]✔ Dashboard executed successfully![/green]")
        console.print(f"[dim]Execution time: {run.execution_time_ms}ms[/dim]")
        console.print(f"[dim]Widgets executed: {len(run.widget_results)}/{len(run.widget_results)}[/dim]")

        # Show any errors
        errors = [r for r in run.widget_results if r.error]
        if errors:
            console.print(f"\n[yellow]Warnings: {len(errors)} widget(s) had errors[/yellow]")
            for err in errors[:3]:
                console.print(f"  [dim]• {err.widget_id}: {err.error}[/dim]")

    except Exception as e:
        console.print(f"[red]Error executing dashboard:[/red] {e}")
        raise click.Abort()


@cli.command("render-dashboard")
@click.argument("dashboard_id")
@click.option("--format", "-f", type=click.Choice(["html", "json"]), default="html", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
@click.option("--execute/--no-execute", default=True, help="Execute queries before rendering")
def render_dashboard(dashboard_id: str, format: str, output: str, execute: bool):
    """Render a dashboard to HTML or JSON.

    Examples:

        kai-agent render-dashboard abc123def456 --format html

        kai-agent render-dashboard abc123def456 --format json -o dashboard.json

        kai-agent render-dashboard abc123def456 --format html -o report.html --execute
    """
    import asyncio
    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    try:
        with console.status(f"[bold cyan]Rendering dashboard to {format.upper()}...[/bold cyan]"):
            result = asyncio.run(service.render(dashboard_id, format=format, execute=execute))

        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(result)
            console.print(f"[green]✔ Dashboard saved to:[/green] {output}")
        else:
            if format == "json":
                console.print(result)
            else:
                console.print(f"[green]✔ Dashboard rendered ({len(result)} bytes)[/green]")
                console.print(f"[dim]Use --output to save to file[/dim]")

    except Exception as e:
        console.print(f"[red]Error rendering dashboard:[/red] {e}")
        raise click.Abort()


@cli.command("delete-dashboard")
@click.argument("dashboard_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete_dashboard(dashboard_id: str, force: bool):
    """Delete a dashboard.

    Examples:

        kai-agent delete-dashboard abc123def456

        kai-agent delete-dashboard abc123def456 -f
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Settings(settings)
    service = DashboardService(storage)

    # Get dashboard for confirmation
    dashboard = service.get(dashboard_id)
    if not dashboard:
        console.print(f"[red]Dashboard not found:[/red] {dashboard_id}")
        return

    if not force:
        console.print(f"[yellow]About to delete dashboard:[/yellow]")
        console.print(f"  Name: {dashboard.name}")
        console.print(f"  ID: {dashboard_id}")
        if not click.confirm("\nDo you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    if service.delete(dashboard_id):
        console.print(f"[green]✔ Dashboard deleted:[/green] {dashboard.name}")
    else:
        console.print(f"[red]Failed to delete dashboard[/red]")


@cli.command("refine-dashboard")
@click.argument("dashboard_id")
@click.argument("request")
def refine_dashboard(dashboard_id: str, request: str):
    """Refine a dashboard using natural language.

    Examples:

        kai-agent refine-dashboard abc123def456 "Add a chart showing monthly revenue"

        kai-agent refine-dashboard abc123def456 "Change the color scheme to blue"
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService
    from app.modules.dashboard.models import RefineDashboardRequest

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    req = RefineDashboardRequest(request=request)

    try:
        with console.status("[bold cyan]Refining dashboard...[/bold cyan]"):
            dashboard = asyncio.run(service.refine(dashboard_id, req))

        console.print(Panel(
            f"[bold green]✔ Dashboard refined successfully![/bold green]\\n\\n"
            f"[cyan]Name:[/cyan] {dashboard.name}\\n"
            f"[cyan]Widgets:[/cyan] {len(dashboard.layout.widgets)}",
            title="Dashboard Refined",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error refining dashboard:[/red] {e}")
        raise click.Abort()


# ============================================================================
# MDL (Semantic Layer) Commands
# ============================================================================

@click.group()
def mdl():
    """MDL (semantic layer) management commands.
    
    The MDL provides semantic context that improves KAI's reasoning about
    your data, including relationships, calculated fields, and business
    terminology.
    """
    pass


def _run_async(coro):
    """Bridge async functions in synchronous Click context."""
    return asyncio.run(coro)


def _resolve_manifest_identifier(
    identifier: str, 
    mdl_service, 
    db_repo
) -> tuple[str, object] | None:
    """Resolve manifest identifier to manifest ID and database connection.
    
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
    db_conn = db_repo.find_by_alias(identifier)
    if db_conn:
        manifest = _run_async(
            mdl_service.get_manifest_by_db_connection(db_conn.id)
        )
        if manifest:
            return manifest.id, db_conn
    
    # Try as database connection ID
    db_conn = db_repo.find_by_id(identifier)
    if db_conn:
        manifest = _run_async(
            mdl_service.get_manifest_by_db_connection(db_conn.id)
        )
        if manifest:
            return manifest.id, db_conn
    
    return None


@mdl.command("list")
@click.option("--db", "db_identifier", help="Filter by database connection ID or alias")
def mdl_list(db_identifier: str | None):
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
    from rich.table import Table
    from rich.box import MINIMAL_DOUBLE_HEAD
    
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
        db_conn = db_repo.find_by_alias(db_identifier)
        if not db_conn:
            db_conn = db_repo.find_by_id(db_identifier)
        if not db_conn:
            console.print(f"[red]Database connection '{db_identifier}' not found[/red]")
            console.print("[dim]Tip: Use 'kai-agent list-connections' to see available databases[/dim]")
            return
        db_connection_id = db_conn.id
    
    # Fetch manifests
    manifests = _run_async(
        mdl_service.list_manifests(db_connection_id=db_connection_id)
    )
    
    if not manifests:
        if db_connection_id:
            console.print(f"[yellow]No MDL manifests found for database '{db_identifier}'[/yellow]")
            console.print("[dim]Tip: Use 'kai-agent scan-all --generate-mdl' to create one[/dim]")
        else:
            console.print("[yellow]No MDL manifests found[/yellow]")
            console.print("[dim]Tip: Use 'kai-agent scan-all <db> --generate-mdl' to create one[/dim]")
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
def mdl_show(manifest_identifier: str, summary: bool, format: str, output: str | None):
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
    from rich.panel import Panel
    from rich.table import Table
    from rich.box import MINIMAL_DOUBLE_HEAD
    import json
    from pathlib import Path
    
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


def _display_manifest_terminal(manifest, db_conn, summary: bool):
    """Display manifest in Rich terminal format."""
    from rich.panel import Panel
    from rich.table import Table
    from rich.box import MINIMAL_DOUBLE_HEAD
    
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


# Add mdl group to main CLI
cli.add_command(mdl)


if __name__ == "__main__":
    cli()
