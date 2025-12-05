"""SQL query execution tools."""
import json
import decimal
import uuid
from datetime import datetime, date
from app.utils.sql_database.sql_database import SQLDatabase


def create_sql_query_tool(database: SQLDatabase, max_rows: int = 1000):
    """Create SQL query execution tool."""

    def json_serializer(obj):
        """Custom JSON serializer for SQL types."""
        if isinstance(obj, (decimal.Decimal, float)):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def sql_query(query: str) -> str:
        """Execute a read-only SQL query and return results.

        Args:
            query: SQL SELECT query to execute

        Returns:
            JSON string with query results and metadata
        """
        try:
            result = database.run_sql(query, max_rows)
            rows = result[1].get("result", []) if isinstance(result, tuple) else []
            
            # Safely get columns if rows exist
            columns = list(rows[0].keys()) if rows and len(rows) > 0 else []
            
            return json.dumps({
                "success": True,
                "row_count": len(rows),
                "columns": columns,
                "data": rows[:100],
                "truncated": len(rows) > 100,
            }, default=json_serializer)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return sql_query
