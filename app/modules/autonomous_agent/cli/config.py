"""Configuration and system utilities commands."""

import asyncio
import json
import click
from rich.table import Table
from rich.panel import Panel

from app.modules.autonomous_agent.cli import console


@click.group()
def config():
    """Configuration and system utilities.

    These commands provide system information, configuration management,
    and utility functions for the KAI system.
    """
    pass


@config.command("show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def show(as_json: bool):
    """Show current configuration settings.

    Examples:

        kai config show
        kai config show --json
    """
    from app.server.config import Settings

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
            ("AGENT_LANGUAGE", getattr(settings, "AGENT_LANGUAGE", "en")),
            ("AGENT_MAX_ITERATIONS", settings.AGENT_MAX_ITERATIONS),
            ("SQL_EXECUTION_TIMEOUT", settings.SQL_EXECUTION_TIMEOUT),
            ("UPPER_LIMIT_QUERY_RETURN_ROWS", settings.UPPER_LIMIT_QUERY_RETURN_ROWS),
        ],
        "Memory & Learning": [
            ("MEMORY_BACKEND", getattr(settings, "MEMORY_BACKEND", "typesense")),
            ("ENABLE_AUTO_LEARNING", getattr(settings, "ENABLE_AUTO_LEARNING", False)),
            ("AUTO_LEARNING_CAPTURE_ONLY", getattr(settings, "AUTO_LEARNING_CAPTURE_ONLY", False)),
        ],
        "Integrations": [
            ("MCP_ENABLED", getattr(settings, "MCP_ENABLED", False)),
            ("MCP_SERVERS_CONFIG", getattr(settings, "MCP_SERVERS_CONFIG", None)),
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


@config.command("check")
def check():
    """Check environment variables and API keys.

    Validates that required environment variables are set and API keys are configured.

    Examples:

        kai config check
    """
    from app.server.config import Settings

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
        ("LETTA_API_KEY", getattr(settings, "LETTA_API_KEY", None), False, "Letta AI memory backend"),
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


def _get_version() -> str:
    """Get version from pyproject.toml.

    Returns:
        Version string
    """
    try:
        import tomllib
        from pathlib import Path

        # Try to find pyproject.toml
        for parent in [Path(__file__).parent.parent.parent, Path.cwd()]:
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


@config.command("version")
def version():
    """Show KAI Agent version information.

    Examples:

        kai config version
    """
    ver = _get_version()

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


@config.command("worker")
def worker():
    """Start the KAI Temporal Worker.

    Examples:

        kai config worker
    """
    from app.worker_main import main
    asyncio.run(main)
