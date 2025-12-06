"""Rich output utilities."""

from app.utils.rich_output.formatter import (
    console,
    format_number,
    get_spinner,
    print_error,
    print_info,
    print_panel,
    print_python,
    print_sql,
    print_success,
    print_warning,
)
from app.utils.rich_output.tables import (
    dataframe_to_table,
    dict_to_table,
    print_dataframe,
    print_dict,
)

__all__ = [
    "console",
    "dataframe_to_table",
    "dict_to_table",
    "format_number",
    "get_spinner",
    "print_dataframe",
    "print_dict",
    "print_error",
    "print_info",
    "print_panel",
    "print_python",
    "print_sql",
    "print_success",
    "print_warning",
]
