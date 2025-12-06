"""Rich table formatting utilities."""

from __future__ import annotations

from typing import Any

import pandas as pd
from rich.console import Console
from rich.table import Table

from app.utils.rich_output.formatter import format_number


console = Console()


def dataframe_to_table(
    df: pd.DataFrame,
    title: str | None = None,
    max_rows: int = 50,
    show_index: bool = False,
) -> Table:
    """Convert DataFrame to Rich table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    if show_index:
        table.add_column("Index", style="dim")

    for col in df.columns:
        table.add_column(str(col))

    display_df = df.head(max_rows)

    for idx, row in display_df.iterrows():
        row_values = []
        if show_index:
            row_values.append(str(idx))

        for val in row:
            if pd.isna(val):
                row_values.append("[dim]NULL[/dim]")
            elif isinstance(val, float):
                row_values.append(format_number(val))
            else:
                row_values.append(str(val))

        table.add_row(*row_values)

    if len(df) > max_rows:
        table.add_row(
            *["..." for _ in range(len(df.columns) + (1 if show_index else 0))]
        )

    return table


def print_dataframe(
    df: pd.DataFrame,
    title: str | None = None,
    max_rows: int = 50,
) -> None:
    """Print DataFrame as formatted table."""
    table = dataframe_to_table(df, title=title, max_rows=max_rows)
    console.print(table)
    if len(df) > max_rows:
        console.print(f"[dim]Showing {max_rows} of {len(df)} rows[/dim]")


def dict_to_table(
    data: dict[str, Any],
    title: str | None = None,
) -> Table:
    """Convert dictionary to key-value table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Key", style="bold")
    table.add_column("Value")

    for key, value in data.items():
        if isinstance(value, float):
            table.add_row(str(key), format_number(value))
        else:
            table.add_row(str(key), str(value))

    return table


def print_dict(data: dict[str, Any], title: str | None = None) -> None:
    """Print dictionary as formatted table."""
    table = dict_to_table(data, title=title)
    console.print(table)
