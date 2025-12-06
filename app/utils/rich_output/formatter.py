"""Rich output formatting utilities."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax


console = Console()


def print_panel(
    content: str,
    title: str | None = None,
    style: str = "blue",
) -> None:
    """Print content in a styled panel."""
    console.print(Panel(content, title=title, border_style=style))


def print_sql(sql: str, title: str = "SQL Query") -> None:
    """Print SQL with syntax highlighting."""
    syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="green"))


def print_python(code: str, title: str = "Python") -> None:
    """Print Python code with syntax highlighting."""
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="yellow"))


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]\u2713[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]\u2717[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]\u26a0[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]\u2139[/blue] {message}")


def get_spinner() -> Progress:
    """Get a spinner progress indicator."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with thousands separator."""
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:,.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:,.{decimals}f}K"
    return f"{value:,.{decimals}f}"
