"""CLI for KAI Autonomous Agent - Intelligent Business Advisor.

Usage:
    # Run analysis queries
    kai-agent run "Analyze sales by region" --db conn_123
    kai-agent run "Show top customers" --db conn_123 --mode query
    kai-agent interactive --db conn_123

    # Database connection management
    kai-agent list-connections
    kai-agent test-connection "postgresql://user:pass@host:5432/db"
    kai-agent create-connection "postgresql://user:pass@host:5432/db" -a my_database
    kai-agent create-connection "postgresql://user:pass@host:5432/db" -a my_db -s public -s analytics
    kai-agent show-connection <connection_id>
    kai-agent update-connection <connection_id> --alias new_name
    kai-agent delete-connection <connection_id>

    # Table management
    kai-agent list-tables <connection_id>
    kai-agent list-tables <connection_id> --schema public --status not_scanned
    kai-agent show-table <table_id>
    kai-agent refresh-tables <connection_id>
    kai-agent scan-tables <connection_id>
    kai-agent scan-tables <connection_id> --with-descriptions --model-family openai
    kai-agent scan-all <connection_id>                    # Refresh + scan all tables
    kai-agent scan-all <connection_id> -d --model-family openai  # With AI descriptions

    # Database context (load before queries/analysis)
    kai-agent db-context <connection_id>                  # Display schema info
    kai-agent db-context <connection_id> -s -d            # With samples + DDL
    kai-agent db-context <connection_id> -f markdown -o context.md  # Export

    # Search tables/columns
    kai-agent search-tables <connection_id> "kpi"         # Search for 'kpi' anywhere
    kai-agent search-tables <connection_id> "*_id"        # Columns ending with _id
    kai-agent search-tables <connection_id> "user*" -i columns  # Search only column names
    kai-agent search-tables <connection_id> "revenue" -i descriptions  # Search descriptions

    # Business glossary management
    kai-agent add-glossary <connection_id> --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"
    kai-agent add-glossary <connection_id> -m "MRR" -s "SELECT SUM(amount) FROM subscriptions WHERE status='active'" --alias "Monthly Recurring Revenue"
    kai-agent list-glossaries <connection_id>
    kai-agent show-glossary <glossary_id>
    kai-agent update-glossary <glossary_id> --sql "SELECT SUM(amount) FROM orders WHERE status='completed'"
    kai-agent delete-glossary <glossary_id>

    # Custom instructions management
    kai-agent add-instruction <connection_id> -c "Always" -r "Format currency with $" --default
    kai-agent add-instruction <connection_id> -c "When asked about revenue" -r "Use revenue_by_month view"
    kai-agent list-instructions <connection_id>
    kai-agent list-instructions <connection_id> --type default
    kai-agent show-instruction <instruction_id>
    kai-agent update-instruction <instruction_id> --rules "New rules"
    kai-agent delete-instruction <instruction_id>

    # Skills management
    kai-agent discover-skills <connection_id> --path ./.skills
    kai-agent list-skills <connection_id>
    kai-agent show-skill <connection_id> <skill_id>
    kai-agent search-skills <connection_id> "revenue analysis"
    kai-agent reload-skill <connection_id> <skill_id> --path ./.skills
    kai-agent delete-skill <connection_id> <skill_id>

    # Memory management (long-term memory across conversations)
    kai-agent list-memories <connection_id>
    kai-agent list-memories <connection_id> --namespace user_preferences
    kai-agent show-memory <connection_id> <namespace> <key>
    kai-agent search-memories <connection_id> "date format preferences"
    kai-agent add-memory <connection_id> user_preferences date_format "Use YYYY-MM-DD"
    kai-agent delete-memory <connection_id> <namespace> <key>
    kai-agent clear-memories <connection_id> --namespace user_preferences
    kai-agent list-namespaces <connection_id>

    # Session management (conversation history)
    kai-agent list-sessions                               # List all sessions
    kai-agent list-sessions --db conn_123                 # Filter by database
    kai-agent list-sessions --status idle                 # Filter by status
    kai-agent show-session <session_id>                   # View session details
    kai-agent delete-session <session_id>                 # Delete a session
    kai-agent export-session <session_id> -o chat.json    # Export to JSON
    kai-agent export-session <session_id> -f markdown     # Export to Markdown
    kai-agent clear-sessions                              # Delete all sessions
    kai-agent clear-sessions --db conn_123                # Delete sessions for DB

    # Configuration & diagnostics
    kai-agent config                                      # Show current config
    kai-agent config --json                               # Output as JSON
    kai-agent env-check                                   # Validate environment
    kai-agent version                                     # Show version info

    # MDL Semantic Layer management
    kai-agent mdl-list <connection_id>                    # List MDL manifests
    kai-agent mdl-show <manifest_id>                      # Show manifest details
    kai-agent mdl-export <manifest_id>                    # Export as WrenAI JSON
    kai-agent mdl-export <manifest_id> -o manifest.json   # Export to file
    kai-agent mdl-delete <manifest_id>                    # Delete manifest
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


@click.group()
def cli():
    """KAI Autonomous Agent - AI-powered data analysis."""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option(
    "--mode",
    type=click.Choice(["full_autonomy", "analysis", "query", "script"]),
    default="full_autonomy",
    help="Agent operation mode",
)
@click.option("--session", "session_id", help="Resume existing session (use session ID from previous run)")
@click.option("--output", "-o", type=click.Path(), help="Save result to file")
@click.option("--stream/--no-stream", default=True, help="Stream output")
def run(prompt: str, db_connection_id: str, mode: str, session_id: str, output: str, stream: bool):
    """Run an autonomous analysis task.

    Examples:

        kai-agent run "What are the top 10 products by revenue?" --db conn_123

        kai-agent run "Analyze customer churn patterns" --db conn_123 --mode analysis

        kai-agent run "Continue the analysis" --db conn_123 --session sess_abc123def456
    """
    asyncio.run(_run_task(prompt, db_connection_id, mode, output, stream, session_id))


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
    asyncio.run(_run_task(prompt, db_connection_id, mode, output, stream, session_id))


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


async def _render_stream(service, task, console) -> str | None:
    """Helper to stream and render agent events.

    Returns the final answer text for use in correction context tracking.
    """
    from rich.console import Group

    output_text = ""
    agent_stack = ["KAI"] # Track active agent context

    # Track todos for pinned display
    current_todos = []

    # Track if we're currently processing (for spinner)
    is_processing = True

    def build_live_content():
        """Build the live display content with pinned todos and spinner."""
        parts = []
        # Pinned todos at top
        todo_panel = _render_todos(current_todos)
        if todo_panel:
            parts.append(todo_panel)
        # Current streaming content - use Markdown for tables
        if output_text.strip():
            try:
                parts.append(Markdown(output_text))
            except Exception:
                parts.append(Text(output_text))
        elif is_processing:
            # Show spinner when no content yet but still processing
            parts.append(Spinner("dots", text="Thinking...", style="cyan"))
        return Group(*parts) if parts else Text("")

    with Live(console=console, refresh_per_second=10, vertical_overflow="visible", transient=False) as live:
        event_count = 0
        async for event in service.stream_execute(task):
            event_count += 1
            
            if event["type"] == "token":
                # Content is always normalized to string by _process_event
                output_text += str(event["content"])
                live.update(build_live_content())

            elif event["type"] == "memory_loaded":
                # Memory loaded silently - no panel display
                pass

            elif event["type"] == "skill_loaded":
                # Skills loaded silently - no panel display
                pass

            elif event["type"] == "todo_update":
                # Update our local list of todos - they stay pinned at top
                new_todos = event.get("todos", [])
                if new_todos:
                    current_todos = new_todos
                    live.update(build_live_content())

            elif event["type"] == "tool_start":
                tool_name = event['tool']
                tool_input = event.get('input')
                
                # Don't clear output for write_todos - it's just progress tracking
                if tool_name != "write_todos":
                    # Discard reasoning/thought block - we don't display it
                    if output_text.strip():
                        output_text = ""
                        live.update(build_live_content())
                
                if tool_name == "task":
                    # This is a subagent call
                    agent_name = tool_input.get("agent") or tool_input.get("name") or "subagent"
                    agent_stack.append(agent_name)
                    
                    prompt = tool_input.get("prompt", "")
                    live.console.print(f"\n[bold blue]➤ Delegating to {agent_name}[/bold blue]")
                    # Use a Panel for the prompt - use Text to avoid markup parsing errors
                    live.console.print(Panel(Text(prompt), title=f"{agent_name} Task", border_style="blue", title_align="left"))
                elif tool_name == "write_todos":
                    # We handle todo updates via the dedicated event type, but we can acknowledge the tool call briefly
                    pass 
                else:
                    # Normal tool call
                    prefix = "  " * (len(agent_stack) - 1)
                    live.console.print(f"\n{prefix}[bold cyan]➜ Calling tool: {tool_name}[/bold cyan]")
                    if tool_input:
                        if isinstance(tool_input, dict):
                            # Pretty print args, skip internal keys and truncate long values
                            skip_keys = {"runtime", "config", "state", "messages", "memory"}
                            for k, v in tool_input.items():
                                if k in skip_keys:
                                    continue
                                # Truncate long values for display
                                v_str = str(v)
                                if len(v_str) > 200:
                                    v_str = v_str[:200] + "..."
                                # Escape Rich markup in tool input values
                                live.console.print(f"{prefix}[dim]  {k}: {escape_markup(v_str)}[/dim]")
                        else:
                            input_str = str(tool_input)
                            if len(input_str) > 200:
                                input_str = input_str[:200] + "..."
                            # Escape Rich markup in tool input
                            live.console.print(f"{prefix}[dim]  Input: {escape_markup(input_str)}[/dim]")
            
            elif event["type"] == "tool_end":
                tool_name = event['tool']
                output = event.get('output', '')
                
                if tool_name == "task":
                    finished_agent = agent_stack.pop() if len(agent_stack) > 1 else "subagent"
                    live.console.print(f"[bold green]✔ {finished_agent} completed[/bold green]")
                    # Show subagent result - use Text to avoid markup parsing errors
                    live.console.print(Panel(Text(output), title=f"{finished_agent} Result", border_style="blue", title_align="left"))
                elif tool_name == "write_todos":
                    # Skip printing result for write_todos to reduce noise, as we render the list
                    pass
                else:
                    prefix = "  " * (len(agent_stack) - 1)
                    # Truncate long outputs for display but show success
                    display_output = output[:500] + "..." if len(output) > 500 else output
                    live.console.print(f"{prefix}[bold green]✔ {tool_name} result:[/bold green]")
                    # Escape Rich markup in tool output to prevent parsing errors
                    live.console.print(f"{prefix}[dim]{escape_markup(display_output)}[/dim]")

        # End of stream - Final Result
        is_processing = False
        
        # Debug: show event count if no output
        if not output_text.strip():
            live.console.print(f"[dim]Debug: {event_count} events received, no final output[/dim]")
        
        if output_text.strip():
            live.update(Text(""))
            try:
                content = Markdown(output_text)
            except Exception:
                content = Text(output_text)
            live.console.print(Panel(content, title="Analysis / Result", border_style="green", title_align="left"))

    # Return the final answer for tracking (used for correction context)
    return output_text.strip() if output_text else None


async def _run_task(
    prompt: str,
    db_connection_id: str,
    mode: str,
    output: str,
    stream: bool,
    session_id: str | None = None,
):
    """Execute agent task."""
    from app.data.db.storage import Storage
    from app.server.config import Settings  # Direct import, avoid server/__init__.py chain
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

    # Use provided session_id or generate a new one
    is_resume = session_id is not None
    if not session_id:
        session_id = generate_session_id()

    task = AgentTask(
        id=f"cli_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        prompt=prompt,
        db_connection_id=db_connection_id,
        mode=mode,
    )

    # Display session info
    if is_resume:
        console.print(f"[cyan]Resuming session:[/cyan] [bold]{session_id}[/bold]")
    else:
        console.print(f"[cyan]Session:[/cyan] [bold]{session_id}[/bold]")
        console.print(f"[dim]Resume with: kai-agent run \"your prompt\" --db {db_connection_id} --session {session_id}[/dim]")

    console.print(Panel(f"[bold]{escape_markup(prompt)}[/bold]", title=f"KAI Agent [{mode}]"))

    if stream:
        # Streaming execution using new renderer
        await _render_stream(service, task, console)
    else:
        # Non-streaming execution
        with console.status("[bold]Thinking...[/bold]"):
            result = await service.execute(task)

        if result.status == "completed":
            console.print(Panel(Text(result.final_answer), title="Result", border_style="green"))
            console.print(f"[green]Completed in {result.execution_time_ms}ms[/green]")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

        if output and result.final_answer:
            with open(output, "w") as f:
                f.write(result.final_answer)
            console.print(f"[dim]Saved to {output}[/dim]")


@cli.command()
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option("--session", "session_id", help="Resume existing session (use session ID from previous run)")
@click.option("--lang", "language", type=click.Choice(["id", "en"]), default=None, help="Response language: 'id' (Indonesian) or 'en' (English). Defaults to AGENT_LANGUAGE in .env")
def interactive(db_connection_id: str, session_id: str | None, language: str | None):
    """Start an interactive agent session.

    Examples:
        kai-agent interactive --db conn_123

        kai-agent interactive --db conn_123 --session calm-river-472

        kai-agent interactive --db conn_123 --lang id  # Indonesian responses
    """
    asyncio.run(_interactive_session(db_connection_id, session_id, language))


async def _interactive_session(db_connection_id: str, session_id: str | None = None, language: str | None = None):
    """Interactive REPL session.

    Args:
        db_connection_id: Database connection ID
        session_id: Optional session ID for resuming
        language: Response language ('id' or 'en'), defaults to AGENT_LANGUAGE setting
    """
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
    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Database connection not found[/red]")
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
        checkpointer=checkpointer,
        language=language,
    )

    # Determine effective language for display
    effective_lang = language or getattr(settings, "AGENT_LANGUAGE", "id")
    lang_display = "🇮🇩 Bahasa Indonesia" if effective_lang == "id" else "🇬🇧 English"

    console.print(Panel(
        "[bold]KAI Autonomous Agent[/bold]\n"
        f"Language: {lang_display}\n"
        "Type your questions, 'exit' to quit, 'help' for commands\n"
        "Use '/remember <note>' to teach me something",
        title="Interactive Mode"
    ))

    # Use provided session_id (resume mode) or generate a new one
    is_resume = session_id is not None
    if not session_id:
        session_id = generate_session_id()

    if is_resume:
        console.print(f"[cyan]Resuming session:[/cyan] [bold]{session_id}[/bold]\n")
    else:
        console.print(f"[cyan]Session:[/cyan] [bold]{session_id}[/bold]")
        console.print(f"[dim]Resume later with: kai-agent interactive --db {db_connection_id} --session {session_id}[/dim]\n")

    # Track previous answer for correction context
    previous_answer: str | None = None

    while True:
        try:
            prompt = console.input("\n[bold cyan]kai>[/bold cyan] ").strip()

            if not prompt:
                continue
            if prompt.lower() == "exit":
                # Save session before exiting
                with console.status("[dim]Saving session...[/dim]"):
                    await service.save_session(session_id)
                break
            if prompt.lower() == "help":
                console.print("""[bold]Commands:[/bold]
  exit              - Exit the session
  help              - Show this help
  clear             - Clear the screen
  /paste            - Enter multi-line paste mode (end with '.' on new line)
  /remember <note>  - Teach me something to remember for future sessions
                      Example: /remember Java province should include Yogyakarta
  /copy             - Copy the last answer to clipboard
  /raw              - Print last answer as raw text (easier to copy)
  /forget           - (not implemented yet)

[bold]Tips:[/bold]
  - Use /paste to paste long multi-line text
  - Start with triple quotes (''') to enter multi-line mode

[bold]Corrections:[/bold]
  I automatically learn from corrections! Just say things like:
  - "Actually, you should include Yogyakarta"
  - "That's wrong, the column is 'total_members' not 'members'"
  - "You forgot to filter by active status"
""")
                continue
            if prompt.lower() == "clear":
                console.clear()
                continue

            # Handle /paste command - multi-line input mode
            if prompt.lower() == "/paste":
                console.print("[dim]Paste mode: Enter your text, then type '.' on a new line to submit[/dim]")
                lines = []
                while True:
                    line = console.input("[dim]...[/dim] ")
                    if line.strip() == ".":
                        break
                    lines.append(line)
                prompt = "\n".join(lines)
                if not prompt.strip():
                    console.print("[yellow]Empty input, cancelled.[/yellow]")
                    continue
                console.print(f"[dim]Received {len(lines)} lines[/dim]")
                # Fall through to process the prompt

            # Handle triple-quote multi-line input (''' or """)
            if prompt.startswith("'''") or prompt.startswith('"""'):
                quote_char = prompt[:3]
                if prompt.endswith(quote_char) and len(prompt) > 6:
                    # Single line with quotes, strip them
                    prompt = prompt[3:-3]
                else:
                    # Multi-line mode - collect until closing quotes
                    console.print(f"[dim]Multi-line mode: End with {quote_char}[/dim]")
                    lines = [prompt[3:]]  # Start with text after opening quotes
                    while True:
                        line = console.input("[dim]...[/dim] ")
                        if line.rstrip().endswith(quote_char):
                            lines.append(line.rstrip()[:-3])
                            break
                        lines.append(line)
                    prompt = "\n".join(lines)
                    console.print(f"[dim]Received {len(lines)} lines[/dim]")

            # Handle /copy command - copy last answer to clipboard
            if prompt.lower() == "/copy":
                if previous_answer:
                    import subprocess
                    import platform
                    try:
                        if platform.system() == "Darwin":
                            subprocess.run(["pbcopy"], input=previous_answer.encode(), check=True)
                        elif platform.system() == "Linux":
                            subprocess.run(["xclip", "-selection", "clipboard"], input=previous_answer.encode(), check=True)
                        else:
                            # Windows
                            subprocess.run(["clip"], input=previous_answer.encode(), check=True)
                        console.print("[green]✓ Copied to clipboard![/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to copy: {e}[/red]")
                        console.print("[dim]Use /raw to print raw text for manual copying[/dim]")
                else:
                    console.print("[yellow]No answer to copy yet. Ask a question first.[/yellow]")
                continue

            # Handle /raw command - print raw text for easy copying
            if prompt.lower() == "/raw":
                if previous_answer:
                    console.print("\n[dim]─── Raw Answer (select and copy) ───[/dim]")
                    console.print(Text(previous_answer))
                    console.print("[dim]─── End of Answer ───[/dim]\n")
                else:
                    console.print("[yellow]No answer to show yet. Ask a question first.[/yellow]")
                continue

            # Handle /remember command for manual learning
            if prompt.lower().startswith("/remember "):
                note = prompt[10:].strip()
                if note:
                    from app.modules.autonomous_agent.learning import (
                        remember_correction_async,
                        get_learning_client,
                        detect_correction_category,
                    )
                    console.print(f"[yellow]Remembering:[/yellow] {escape_markup(note)}")

                    # Try Letta first, fall back to Typesense
                    if get_learning_client() is not None:
                        result = await remember_correction_async(
                            db_connection_id=db_connection_id,
                            session_id=session_id,
                            correction=note,
                            context=previous_answer,
                        )
                        if result:
                            console.print("[green]✓ Noted! I'll remember this for future sessions (Letta).[/green]")
                        else:
                            console.print("[red]Failed to save to Letta.[/red]")
                    else:
                        # Use Typesense memory service as fallback
                        category = detect_correction_category(note)
                        service.memory_service.remember_correction(
                            db_connection_id=db_connection_id,
                            correction=note,
                            context=previous_answer,
                            session_id=session_id,
                            category=category,
                        )
                        console.print("[green]✓ Noted! I'll remember this for future sessions (Typesense).[/green]")
                else:
                    console.print("[yellow]Usage: /remember <something to remember>[/yellow]")
                continue

            task = AgentTask(
                id=f"cli_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                prompt=prompt,
                db_connection_id=db_connection_id,
                context={"previous_answer": previous_answer} if previous_answer else None,
            )

            # Capture the answer for next iteration's context
            try:
                answer = await _render_stream(service, task, console)
                if answer:
                    previous_answer = answer
            except Exception as stream_error:
                console.print(f"[red]Stream error: {stream_error}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Press Ctrl+C again to exit or continue chatting.[/yellow]")
            try:
                # Wait for another Ctrl+C or let user continue
                prompt = console.input("\n[bold cyan]kai>[/bold cyan] ").strip()
                if prompt.lower() == "exit":
                    with console.status("[dim]Saving session...[/dim]"):
                        await service.save_session(session_id)
                    break
                # User continued, process the new prompt
                continue
            except KeyboardInterrupt:
                # Double Ctrl+C - save and exit
                console.print("\n[dim]Exiting...[/dim]")
                with console.status("[dim]Saving session...[/dim]"):
                    await service.save_session(session_id)
                break
        except EOFError:
            # Save session on Ctrl+D
            with console.status("[dim]Saving session...[/dim]"):
                await service.save_session(session_id)
            break

    console.print(f"\n[dim]Session ended. Resume with: --session {session_id}[/dim]")


@cli.command()
def list_connections():
    """List available database connections."""
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


@cli.command()
@click.argument("connection_uri")
@click.option("--alias", "-a", required=True, help="Human-readable name for the connection")
@click.option("--schema", "-s", "schemas", multiple=True, default=["public"], help="Database schema(s) to use (can be specified multiple times)")
@click.option("--metadata", "-m", type=str, help="JSON metadata for the connection")
def create_connection(connection_uri: str, alias: str, schemas: tuple, metadata: str):
    """Create a new database connection.

    Examples:

        kai-agent create-connection "postgresql://user:pass@localhost:5432/mydb" -a my_database

        kai-agent create-connection "postgresql://user:pass@host:5432/db" -a prod_db -s public -s analytics

        kai-agent create-connection "csv://data.csv" -a sales_data
    """
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

        console.print(f"\n[green]✔ Connection created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {db_connection.id}\n"
            f"[bold]Alias:[/bold] {db_connection.alias}\n"
            f"[bold]Dialect:[/bold] {db_connection.dialect}\n"
            f"[bold]Schemas:[/bold] {', '.join(db_connection.schemas)}",
            title="Connection Details",
            border_style="green"
        ))
        console.print(f"\n[dim]Use this ID with: kai-agent run \"your query\" --db {db_connection.id}[/dim]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to create connection:[/red] {str(e)}")


@cli.command()
@click.argument("db_connection_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_connection(db_connection_id: str, force: bool):
    """Delete a database connection.

    Example:

        kai-agent delete-connection abc123

        kai-agent delete-connection abc123 --force
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.database_connection.services import DatabaseConnectionService
    from app.utils.sql_database.scanner import SqlAlchemyScanner

    settings = Settings()
    storage = Storage(settings)
    scanner = SqlAlchemyScanner()
    service = DatabaseConnectionService(scanner, storage)

    # Check if connection exists
    db_connection = service.repository.find_by_id(db_connection_id)
    if not db_connection:
        console.print(f"[red]Error:[/red] Connection '{db_connection_id}' not found")
        return

    console.print(f"[bold]Connection to delete:[/bold]")
    console.print(f"  ID: {db_connection.id}")
    console.print(f"  Alias: {db_connection.alias}")
    console.print(f"  Dialect: {db_connection.dialect}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this connection?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        with console.status("[bold cyan]Deleting connection and associated tables...[/bold cyan]"):
            service.delete_database_connection(db_connection_id)

        console.print(f"\n[green]✔ Connection '{db_connection.alias}' deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete connection:[/red] {str(e)}")


@cli.command()
@click.argument("connection_uri")
def test_connection(connection_uri: str):
    """Test a database connection without saving it.

    Examples:

        kai-agent test-connection "postgresql://user:pass@localhost:5432/mydb"

        kai-agent test-connection "csv://path/to/data.csv"
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

        console.print(f"\n[green]✔ Connection successful![/green]")
        console.print(f"[bold]Dialect:[/bold] {sql_database.dialect}")
        console.print(f"[bold]Tables found:[/bold] {len(tables)}")
        if tables:
            console.print(f"  {', '.join(tables[:10])}" + ("..." if len(tables) > 10 else ""))
        if views:
            console.print(f"[bold]Views found:[/bold] {len(views)}")
            console.print(f"  {', '.join(views[:10])}" + ("..." if len(views) > 10 else ""))

    except Exception as e:
        console.print(f"\n[red]✖ Connection failed:[/red] {str(e)}")


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


# =============================================================================
# Configuration Commands
# =============================================================================

@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def config(as_json: bool):
    """Show current configuration settings.

    Examples:

        kai-agent config

        kai-agent config --json
    """
    from app.server.config import Settings
    from rich.table import Table

    settings = Settings()

    # Define categories of settings to show (exclude sensitive ones)
    categories = {
        "Application": [
            ("APP_NAME", settings.APP_NAME),
            ("APP_VERSION", settings.APP_VERSION),
            ("APP_ENVIRONMENT", settings.APP_ENVIRONMENT),
            ("APP_HOST", settings.APP_HOST),
            ("APP_PORT", settings.APP_PORT),
        ],
        "LLM Configuration": [
            ("CHAT_FAMILY", settings.CHAT_FAMILY),
            ("CHAT_MODEL", settings.CHAT_MODEL),
            ("EMBEDDING_FAMILY", settings.EMBEDDING_FAMILY),
            ("EMBEDDING_MODEL", settings.EMBEDDING_MODEL),
            ("EMBEDDING_DIMENSIONS", settings.EMBEDDING_DIMENSIONS),
        ],
        "Agent Settings": [
            ("AGENT_LANGUAGE", settings.AGENT_LANGUAGE),
            ("AGENT_MAX_ITERATIONS", settings.AGENT_MAX_ITERATIONS),
            ("SQL_EXECUTION_TIMEOUT", settings.SQL_EXECUTION_TIMEOUT),
            ("UPPER_LIMIT_QUERY_RETURN_ROWS", settings.UPPER_LIMIT_QUERY_RETURN_ROWS),
        ],
        "Memory & Learning": [
            ("MEMORY_BACKEND", settings.MEMORY_BACKEND),
            ("ENABLE_AUTO_LEARNING", settings.ENABLE_AUTO_LEARNING),
            ("AUTO_LEARNING_CAPTURE_ONLY", settings.AUTO_LEARNING_CAPTURE_ONLY),
        ],
        "Integrations": [
            ("MCP_ENABLED", settings.MCP_ENABLED),
            ("MCP_SERVERS_CONFIG", settings.MCP_SERVERS_CONFIG),
            ("TYPESENSE_HOST", settings.TYPESENSE_HOST),
            ("TYPESENSE_PORT", settings.TYPESENSE_PORT),
        ],
    }

    if as_json:
        config_dict = {}
        for category, items in categories.items():
            config_dict[category] = {k: v for k, v in items}
        console.print(json.dumps(config_dict, indent=2, default=str))
        return

    for category, items in categories.items():
        table = Table(title=category, show_header=True, header_style="bold")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in items:
            value_str = str(value) if value is not None else "[dim]not set[/dim]"
            table.add_row(key, value_str)

        console.print(table)
        console.print()


@cli.command()
def env_check():
    """Check environment variables and API keys.

    Validates that required environment variables are set and API keys are configured.

    Examples:

        kai-agent env-check
    """
    from app.server.config import Settings
    from rich.table import Table

    settings = Settings()

    checks = [
        # Required
        ("TYPESENSE_API_KEY", settings.TYPESENSE_API_KEY, True, "Vector search storage"),
        ("ENCRYPT_KEY", settings.ENCRYPT_KEY, True, "Database credential encryption"),

        # LLM Providers (at least one required)
        ("OPENAI_API_KEY", settings.OPENAI_API_KEY, False, "OpenAI models (GPT-4, etc.)"),
        ("GOOGLE_API_KEY", settings.GOOGLE_API_KEY, False, "Google Gemini models"),
        ("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY, False, "OpenRouter multi-provider"),
        ("OLLAMA_API_BASE", settings.OLLAMA_API_BASE, False, "Ollama local models"),

        # Optional
        ("LETTA_API_KEY", settings.LETTA_API_KEY, False, "Letta AI memory backend"),
        ("GCS_API_KEY", settings.GCS_API_KEY, False, "Google Cloud Storage"),
    ]

    table = Table(title="Environment Check")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Required", justify="center")
    table.add_column("Purpose", style="dim")

    all_required_set = True
    any_llm_set = False

    for name, value, required, purpose in checks:
        is_set = value is not None and str(value).strip() != ""

        if is_set:
            status = "[green]✔ Set[/green]"
            if name in ["OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "OLLAMA_API_BASE"]:
                any_llm_set = True
        else:
            if required:
                status = "[red]✘ Missing[/red]"
                all_required_set = False
            else:
                status = "[yellow]○ Not set[/yellow]"

        req_str = "[red]Yes[/red]" if required else "[dim]No[/dim]"
        table.add_row(name, status, req_str, purpose)

    console.print(table)
    console.print()

    # Summary
    if not all_required_set:
        console.print("[red]✘ Some required environment variables are missing![/red]")
        console.print("[dim]Check your .env file and ensure all required variables are set.[/dim]")
    elif not any_llm_set:
        console.print("[yellow]⚠ No LLM provider configured![/yellow]")
        console.print("[dim]Set at least one of: OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY, or OLLAMA_API_BASE[/dim]")
    else:
        console.print("[green]✔ All checks passed![/green]")

    # Show current LLM configuration
    console.print()
    console.print("[bold]Current LLM Configuration:[/bold]")
    console.print(f"  Chat: {settings.CHAT_FAMILY}/{settings.CHAT_MODEL}")
    console.print(f"  Embeddings: {settings.EMBEDDING_FAMILY}/{settings.EMBEDDING_MODEL}")


# =============================================================================
# Version Command
# =============================================================================

def get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        import tomllib
        from pathlib import Path

        # Try to find pyproject.toml
        for parent in [Path(__file__).parent, Path.cwd()]:
            for _ in range(5):  # Look up to 5 levels up
                pyproject = parent / "pyproject.toml"
                if pyproject.exists():
                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                        return data.get("project", {}).get("version", "unknown")
                parent = parent.parent
    except Exception:
        pass
    return "0.1.0"


@cli.command()
def version():
    """Show KAI Agent version information.

    Examples:

        kai-agent version
    """
    from rich.panel import Panel

    ver = get_version()

    info = [
        f"[bold cyan]KAI Agent[/bold cyan] v{ver}",
        "",
        "[dim]AI-powered autonomous data analysis agent[/dim]",
        "",
        "Framework: LangGraph + DeepAgents",
        "Backend: Typesense + LangChain",
        "CLI: Click + Rich",
    ]

    console.print(Panel("\n".join(info), title="Version", border_style="cyan"))


# =============================================================================
# MDL Semantic Layer Commands
# =============================================================================


@cli.command()
@click.argument("db_connection_id")
def mdl_list(db_connection_id: str):
    """List MDL semantic layer manifests for a database connection.

    Examples:

        # List all MDL manifests for a connection
        kai-agent mdl-list abc123
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository
    from rich.table import Table

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)

    try:
        manifests = asyncio.get_event_loop().run_until_complete(
            mdl_repo.list(db_connection_id=db_connection_id)
        )

        if not manifests:
            console.print(f"[yellow]No MDL manifests found for connection '{db_connection_id}'[/yellow]")
            console.print("[dim]Use 'kai-agent scan-all <connection_id> --generate-mdl' to create one[/dim]")
            return

        table = Table(title=f"MDL Manifests ({len(manifests)})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Catalog")
        table.add_column("Schema")
        table.add_column("Models", justify="right")
        table.add_column("Relationships", justify="right")

        for m in manifests:
            table.add_row(
                m.id or "-",
                m.name or "-",
                m.catalog,
                m.schema,
                str(len(m.models)),
                str(len(m.relationships)),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument("manifest_id")
def mdl_show(manifest_id: str):
    """Show details of an MDL manifest.

    Examples:

        # Show manifest details
        kai-agent mdl-show abc123
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository
    from rich.table import Table
    from rich.tree import Tree

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)

    try:
        manifest = asyncio.get_event_loop().run_until_complete(
            mdl_repo.get(manifest_id)
        )

        if not manifest:
            console.print(f"[red]Error:[/red] Manifest '{manifest_id}' not found")
            return

        # Header
        console.print(f"\n[bold cyan]MDL Manifest:[/bold cyan] {manifest.name or manifest_id}")
        console.print(f"[dim]ID: {manifest.id}[/dim]")
        console.print(f"[dim]Database: {manifest.db_connection_id}[/dim]")
        console.print(f"Catalog: {manifest.catalog} | Schema: {manifest.schema}")
        if manifest.data_source:
            console.print(f"Data Source: {manifest.data_source}")
        console.print()

        # Models
        if manifest.models:
            console.print(f"[bold]Models ({len(manifest.models)}):[/bold]")
            for model in manifest.models:
                desc = f" - {model.properties.get('description')}" if model.properties and model.properties.get('description') else ""
                pk = f" (PK: {model.primary_key})" if model.primary_key else ""
                console.print(f"  [green]•[/green] [cyan]{model.name}[/cyan]{pk}{desc}")

                # Show columns (limited)
                if model.columns:
                    col_names = [c.name for c in model.columns[:8]]
                    more = f" +{len(model.columns) - 8} more" if len(model.columns) > 8 else ""
                    console.print(f"    Columns: {', '.join(col_names)}{more}")
            console.print()

        # Relationships
        if manifest.relationships:
            console.print(f"[bold]Relationships ({len(manifest.relationships)}):[/bold]")
            for rel in manifest.relationships:
                jt_map = {"ONE_TO_ONE": "1:1", "ONE_TO_MANY": "1:N", "MANY_TO_ONE": "N:1", "MANY_TO_MANY": "N:N"}
                jt = jt_map.get(rel.join_type.value, rel.join_type.value) if rel.join_type else "?"
                console.print(f"  [green]•[/green] [cyan]{rel.name}[/cyan]: {rel.models[0]} {jt} {rel.models[1]}")
                console.print(f"    [dim]{rel.condition}[/dim]")
            console.print()

        # Metrics
        if manifest.metrics:
            console.print(f"[bold]Metrics ({len(manifest.metrics)}):[/bold]")
            for metric in manifest.metrics:
                desc = f" - {metric.properties.get('description')}" if metric.properties and metric.properties.get('description') else ""
                console.print(f"  [green]•[/green] [cyan]{metric.name}[/cyan]{desc}")
                console.print(f"    Base: {metric.base_object}")
                if metric.measure:
                    for m in metric.measure:
                        expr = m.expression or m.name
                        console.print(f"    Measure: {m.name} = {expr}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument("manifest_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--pretty", "-p", is_flag=True, default=True, help="Pretty print JSON (default: true)")
def mdl_export(manifest_id: str, output: str, pretty: bool):
    """Export MDL manifest as WrenAI-compatible JSON.

    Examples:

        # Print to console
        kai-agent mdl-export abc123

        # Save to file
        kai-agent mdl-export abc123 -o manifest.json

        # Compact JSON (no formatting)
        kai-agent mdl-export abc123 --no-pretty
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository
    from app.modules.mdl.services import MDLService

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)
    mdl_service = MDLService(repository=mdl_repo)

    try:
        mdl_json = asyncio.get_event_loop().run_until_complete(
            mdl_service.export_mdl_json(manifest_id)
        )

        if pretty:
            json_str = json.dumps(mdl_json, indent=2)
        else:
            json_str = json.dumps(mdl_json)

        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            console.print(f"[green]✔[/green] Exported to {output}")
        else:
            console.print(json_str)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument("manifest_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def mdl_delete(manifest_id: str, force: bool):
    """Delete an MDL manifest.

    Examples:

        # Delete with confirmation
        kai-agent mdl-delete abc123

        # Delete without confirmation
        kai-agent mdl-delete abc123 --force
    """
    import asyncio
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.mdl.repositories import MDLRepository

    settings = Settings()
    storage = Storage(settings)
    mdl_repo = MDLRepository(storage=storage)

    try:
        # Check if exists
        manifest = asyncio.get_event_loop().run_until_complete(
            mdl_repo.get(manifest_id)
        )

        if not manifest:
            console.print(f"[red]Error:[/red] Manifest '{manifest_id}' not found")
            return

        # Confirm deletion
        if not force:
            name = manifest.name or manifest_id
            if not click.confirm(f"Delete MDL manifest '{name}'?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        asyncio.get_event_loop().run_until_complete(
            mdl_repo.delete(manifest_id)
        )

        console.print(f"[green]✔[/green] Deleted MDL manifest '{manifest_id}'")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


if __name__ == "__main__":
    cli()
