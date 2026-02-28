"""Query and analysis commands.

This command group contains the core query and analysis functionality
for running autonomous agent tasks, interactive sessions, and debugging.
"""

import asyncio
import uuid
import click
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown

from app.modules.autonomous_agent.cli import console, _run_async


@click.group()
def query():
    """Query and analysis commands.

    Run autonomous analysis tasks, start interactive sessions,
    resume existing conversations, and debug memory injection.
    """
    pass


# ============================================================================
# Helper Functions
# ============================================================================

async def _render_stream(service, task, console):
    """Helper to stream and render agent events."""
    output_text = ""
    agent_stack = ["KAI"]  # Track active agent context

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
                        status = todo.get("status", "pending")
                        content = todo.get("content", "")
                        if status == "completed":
                            icon = "[green]✔[/green]"
                            style = "strike dim"
                        elif status == "in_progress":
                            icon = "[blue]➜[/blue]"
                            style = "bold"
                        else:
                            icon = "[yellow]○[/yellow]"
                            style = ""

                        if style:
                            todo_lines.append(f"{icon} [{style}]{content}[/{style}]")
                        else:
                            todo_lines.append(f"{icon} {content}")

                    if todo_lines:
                        console.print(
                            Panel(
                                "\n".join(todo_lines),
                                title="Todo List",
                                border_style="magenta",
                                title_align="left",
                            )
                        )

            elif event["type"] == "tool_start":
                # Flush reasoning/thought block if exists
                if output_text.strip():
                    current_agent = agent_stack[-1]
                    title = "Reasoning" if current_agent == "KAI" else f"{current_agent} Reasoning"
                    style = "yellow" if current_agent == "KAI" else "blue"

                    # Print ABOVE the live display area
                    console.print(
                        Panel(
                            Markdown(output_text), title=title, border_style=style, title_align="left"
                        )
                    )
                    output_text = ""
                    live.update(Markdown(""))  # Clear live area for next phase

                tool_name = event["tool"]
                tool_input = event.get("input")

                if tool_name == "task":
                    # This is a subagent call
                    agent_name = (
                        tool_input.get("agent") or tool_input.get("name") or "subagent"
                    )
                    agent_stack.append(agent_name)

                    prompt = tool_input.get("prompt", "")
                    console.print(f"\n[bold blue]➤ Delegating to {agent_name}[/bold blue]")
                    # Use a Panel for the prompt to ensure it's clearly visible even if multi-line
                    console.print(
                        Panel(
                            Markdown(prompt),
                            title=f"{agent_name} Task",
                            border_style="blue",
                            title_align="left",
                        )
                    )
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
                tool_name = event["tool"]
                output = event.get("output", "")

                if tool_name == "task":
                    finished_agent = (
                        agent_stack.pop() if len(agent_stack) > 1 else "subagent"
                    )
                    console.print(f"[bold green]✔ {finished_agent} completed[/bold green]")
                    # Show subagent result
                    console.print(
                        Panel(
                            Markdown(output),
                            title=f"{finished_agent} Result",
                            border_style="blue",
                            title_align="left",
                        )
                    )
                elif tool_name == "write_todos":
                    # Skip printing result for write_todos to reduce noise, as we render the list
                    pass
                else:
                    prefix = "  " * (len(agent_stack) - 1)
                    # Truncate long outputs for display but show success
                    display_output = output[:500] + "..." if len(output) > 500 else output
                    console.print(f"{prefix}[bold green]✔ {tool_name} result:[/bold green]")
                    console.print(f"{prefix}[dim]{display_output}[/dim]")

            elif event["type"] == "suggestions":
                console.print("\n[bold cyan]Suggested follow-ups:[/bold cyan]")
                for q in event.get("questions", []):
                    console.print(f"  [dim]>[/dim] {q['question']}")

        # End of stream - Final Result
        if output_text.strip():
            # Clear the live component one last time
            live.update(Markdown(""))
            # Print the final result as a distinct panel
            console.print(
                Panel(
                    Markdown(output_text),
                    title="Analysis / Result",
                    border_style="green",
                    title_align="left",
                )
            )


async def _run_task(prompt: str, db_connection_id: str, mode: str, output: str, stream: bool):
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
        model_family=settings.CHAT_FAMILY or "google",
        model_name=settings.CHAT_MODEL or "gemini-2.0-flash",
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
            db_connection.id = (db_connection.id or "") + "_cli_patched"
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
            console.print(
                Panel(Markdown(result.final_answer), title="Result", border_style="green")
            )
            console.print(f"[green]Completed in {result.execution_time_ms}ms[/green]")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

        if output and result.final_answer:
            with open(output, "w") as f:
                f.write(result.final_answer)
            console.print(f"[dim]Saved to {output}[/dim]")


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
        model_family=settings.CHAT_FAMILY or "google",
        model_name=settings.CHAT_MODEL or "gemini-2.0-flash",
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
            db_connection.id = (db_connection.id or "") + "_cli_patched"
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to patch connection URI: {e}[/yellow]")

    # Create memory checkpointer for multi-turn conversation
    checkpointer = MemorySaver()

    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(
        db_connection, database, llm_config=llm_config, checkpointer=checkpointer
    )

    console.print(
        Panel(
            "[bold]KAI Autonomous Agent[/bold]\n"
            "Type your questions, 'exit' to quit, 'help' for commands",
            title="Interactive Mode",
        )
    )

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


# ============================================================================
# Commands
# ============================================================================


@query.command("run")
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

        kai query run "What are the top 10 products by revenue?" --db conn_123

        kai query run "Analyze customer churn patterns" --db conn_123 --mode analysis
    """
    _run_async(_run_task(prompt, db_connection_id, mode, output, stream))


@query.command("interactive")
@click.option("--db", "db_identifier", required=True, help="Database connection ID or alias")
def interactive(db_identifier: str):
    """Start an interactive agent session.

    Example:
        kai query interactive --db kemenkop
        kai query interactive --db conn_123
    """
    _run_async(_interactive_session(db_identifier))


@query.command("resume")
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
def resume(
    session_id: str, prompt: str, db_connection_id: str, mode: str, output: str, stream: bool
):
    """Resume an existing session with a new prompt.

    SESSION_ID is the session ID from a previous run (e.g., sess_abc123def456).

    Examples:

        kai query resume sess_abc123def456 "Continue analyzing the data" --db conn_123

        kai query resume sess_abc123def456 "What else can you tell me?" --db conn_123
    """
    _run_async(_run_task(prompt, db_connection_id, mode, output, stream))


@query.command("debug")
@click.argument("session_id")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
def debug(session_id: str, db_connection_id: str):
    """Debug memory injection for a session.

    Shows what memory would be injected when resuming a session.

    Example:
        kai query debug calm-river-472 --db conn_123
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
        from agentic_learning import AgenticLearning  # type: ignore[import-untyped]

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
        if hasattr(agent, "memory") and hasattr(agent.memory, "blocks"):
            for block in agent.memory.blocks:
                value_preview = (
                    block.value[:100] + "..."
                    if block.value and len(block.value) > 100
                    else (block.value or "(empty)")
                )
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
