"""Utility functions for detecting corrections in user messages.

This module provides pattern-based detection of correction messages
to identify when users are providing feedback or corrections.
"""

# Patterns that indicate a correction or mistake feedback
CORRECTION_PATTERNS = [
    "actually",
    "that's wrong",
    "that is wrong",
    "incorrect",
    "should be",
    "should include",
    "should not include",
    "you forgot",
    "you missed",
    "missing",
    "wrong column",
    "wrong table",
    "not correct",
    "fix this",
    "correction:",
    "remember:",
    "note:",
    "important:",
]


# Category detection patterns
SQL_PATTERNS = [
    "column", "table", "sql", "query", "select", "where", "join",
    "group by", "order by", "aggregate", "sum", "count", "avg",
]
GEOGRAPHY_PATTERNS = [
    "province", "city", "region", "area", "location", "include",
    "exclude", "java", "yogyakarta", "jakarta", "sumatra", "kalimantan",
    "sulawesi", "papua", "bali", "district", "kabupaten", "kota",
]
DATA_PATTERNS = [
    "filter", "condition", "status", "active", "inactive", "date",
    "range", "period", "year", "month", "quarter",
]


def is_correction_message(message: str) -> bool:
    """Check if a message appears to be a correction or feedback.

    Args:
        message: The user's message.

    Returns:
        True if the message appears to be a correction.
    """
    message_lower = message.lower().strip()
    return any(pattern in message_lower for pattern in CORRECTION_PATTERNS)


def detect_correction_category(message: str) -> str:
    """Detect the category of a correction message.

    Args:
        message: The correction message.

    Returns:
        Category string: 'sql', 'geography', 'data', or 'general'.
    """
    message_lower = message.lower()

    # Check for SQL-related patterns
    if any(pattern in message_lower for pattern in SQL_PATTERNS):
        return "sql"

    # Check for geography-related patterns
    if any(pattern in message_lower for pattern in GEOGRAPHY_PATTERNS):
        return "geography"

    # Check for data filtering patterns
    if any(pattern in message_lower for pattern in DATA_PATTERNS):
        return "data"

    return "general"
