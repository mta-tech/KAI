"""Database schema and context tools."""
import json
import re
import fnmatch
from typing import Optional

from app.modules.database_connection.models import DatabaseConnection
from app.data.db.storage import Storage


def create_schema_context_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create database schema context tool.

    This tool allows the agent to load database schema information
    before running SQL queries or analysis.
    """
    from app.modules.table_description.repositories import TableDescriptionRepository

    table_repo = TableDescriptionRepository(storage)

    def get_database_schema(include_samples: bool = False) -> str:
        """Get the complete database schema including all tables, columns, and their descriptions.

        IMPORTANT: Call this tool FIRST before writing any SQL queries to understand
        the available tables, columns, data types, and relationships.

        Args:
            include_samples: If True, include sample data rows for each table

        Returns:
            JSON string with complete database schema information including:
            - All tables with descriptions
            - All columns with types, descriptions, and constraints
            - Primary and foreign key relationships
            - Low cardinality column values (useful for WHERE clauses)
            - Filterable columns summary for quick reference
            - Sample data (if include_samples=True)
        """
        try:
            tables = table_repo.find_by({"db_connection_id": db_connection.id})

            if not tables:
                return json.dumps({
                    "success": False,
                    "error": "No tables found. Database may not be scanned yet."
                })

            schema_info = {
                "success": True,
                "database": {
                    "alias": db_connection.alias,
                    "dialect": db_connection.dialect,
                    "schemas": db_connection.schemas,
                    "description": db_connection.description,
                },
                "tables": [],
                "filterable_columns": []  # Quick reference for columns with known values
            }

            for table in tables:
                table_info = {
                    "name": table.table_name,
                    "schema": table.db_schema,
                    "full_name": f"{table.db_schema}.{table.table_name}",
                    "description": table.table_description,
                    "columns": []
                }

                for col in (table.columns or []):
                    col_info = {
                        "name": col.name,
                        "type": col.data_type,
                        "description": col.description,
                    }

                    if col.is_primary_key:
                        col_info["primary_key"] = True

                    if col.foreign_key:
                        col_info["foreign_key"] = {
                            "references_table": col.foreign_key.reference_table,
                            "references_column": col.foreign_key.field_name
                        }

                    # Include categorical values for low cardinality columns
                    if col.low_cardinality and col.categories:
                        col_info["filterable"] = True
                        col_info["allowed_values"] = col.categories
                        col_info["cardinality"] = len(col.categories)

                        # Add to filterable columns summary for quick reference
                        schema_info["filterable_columns"].append({
                            "table": f"{table.db_schema}.{table.table_name}",
                            "column": col.name,
                            "type": col.data_type,
                            "values": col.categories,
                            "cardinality": len(col.categories),
                            "hint": f"Use WHERE {col.name} IN ({', '.join(repr(v) for v in col.categories[:5])}{'...' if len(col.categories) > 5 else ''})"
                        })

                    table_info["columns"].append(col_info)

                if include_samples and table.examples:
                    table_info["sample_rows"] = table.examples[:3]

                schema_info["tables"].append(table_info)

            # Add summary for quick reference
            schema_info["summary"] = {
                "total_tables": len(tables),
                "table_names": [t.table_name for t in tables],
                "total_filterable_columns": len(schema_info["filterable_columns"]),
            }

            # Add usage hint
            if schema_info["filterable_columns"]:
                schema_info["filter_usage_hint"] = (
                    "IMPORTANT: When filtering data, use the exact values from 'allowed_values' "
                    "in the filterable_columns list. These are the only valid values for those columns."
                )

            return json.dumps(schema_info, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return get_database_schema


def create_list_tables_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a simple tool to list available tables."""
    from app.modules.table_description.repositories import TableDescriptionRepository

    table_repo = TableDescriptionRepository(storage)

    def list_tables() -> str:
        """List all available tables in the database.

        Returns a quick overview of all tables with their descriptions.
        Use get_database_schema() for detailed column information.

        Returns:
            JSON string with table names and descriptions
        """
        try:
            tables = table_repo.find_by({"db_connection_id": db_connection.id})

            result = {
                "success": True,
                "tables": [
                    {
                        "name": t.table_name,
                        "schema": t.db_schema,
                        "description": t.table_description,
                        "column_count": len(t.columns) if t.columns else 0,
                    }
                    for t in tables
                ]
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return list_tables


def create_get_table_details_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to get details for a specific table."""
    from app.modules.table_description.repositories import TableDescriptionRepository

    table_repo = TableDescriptionRepository(storage)

    def get_table_details(table_name: str) -> str:
        """Get detailed information about a specific table.

        Use this when you need to understand a specific table's structure
        before writing a query involving that table.

        Args:
            table_name: Name of the table (e.g., 'users' or 'public.users')

        Returns:
            JSON string with table details including columns, types,
            constraints, and sample data
        """
        try:
            tables = table_repo.find_by({"db_connection_id": db_connection.id})

            # Find matching table (check both with and without schema prefix)
            target_table = None
            for t in tables:
                if t.table_name == table_name or f"{t.db_schema}.{t.table_name}" == table_name:
                    target_table = t
                    break

            if not target_table:
                available = [t.table_name for t in tables]
                return json.dumps({
                    "success": False,
                    "error": f"Table '{table_name}' not found",
                    "available_tables": available
                })

            result = {
                "success": True,
                "table": {
                    "name": target_table.table_name,
                    "schema": target_table.db_schema,
                    "full_name": f"{target_table.db_schema}.{target_table.table_name}",
                    "description": target_table.table_description,
                    "columns": [],
                    "ddl": target_table.table_schema,
                    "sample_data": target_table.examples[:5] if target_table.examples else []
                }
            }

            for col in (target_table.columns or []):
                col_info = {
                    "name": col.name,
                    "type": col.data_type,
                    "description": col.description,
                    "is_primary_key": col.is_primary_key,
                    "is_low_cardinality": col.low_cardinality,
                }

                if col.foreign_key:
                    col_info["foreign_key"] = {
                        "references_table": col.foreign_key.reference_table,
                        "references_column": col.foreign_key.field_name
                    }

                if col.low_cardinality and col.categories:
                    col_info["allowed_values"] = col.categories

                result["table"]["columns"].append(col_info)

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return get_table_details


def create_get_filterable_columns_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to get all columns with known categorical values."""
    from app.modules.table_description.repositories import TableDescriptionRepository

    table_repo = TableDescriptionRepository(storage)

    def get_filterable_columns(table_name: str = None) -> str:
        """Get columns that have known categorical values for filtering.

        Use this to find the exact values you can use in WHERE clauses.
        These columns have low cardinality (few distinct values) making them
        ideal for filtering operations.

        Args:
            table_name: Optional - filter to specific table (e.g., 'orders' or 'public.orders')

        Returns:
            JSON with all filterable columns and their allowed values.
            Use these exact values in your SQL WHERE clauses.
        """
        try:
            tables = table_repo.find_by({"db_connection_id": db_connection.id})

            if not tables:
                return json.dumps({
                    "success": False,
                    "error": "No tables found. Database may not be scanned yet."
                })

            filterable = []

            for table in tables:
                # Filter by table name if specified
                if table_name:
                    table_lower = table_name.lower()
                    if (table.table_name.lower() != table_lower and
                        f"{table.db_schema}.{table.table_name}".lower() != table_lower):
                        continue

                for col in (table.columns or []):
                    if col.low_cardinality and col.categories:
                        filterable.append({
                            "table": f"{table.db_schema}.{table.table_name}",
                            "column": col.name,
                            "data_type": col.data_type,
                            "description": col.description,
                            "allowed_values": col.categories,
                            "cardinality": len(col.categories),
                            "sql_example": f"WHERE {col.name} = '{col.categories[0]}'" if col.categories else None,
                            "sql_in_example": f"WHERE {col.name} IN ({', '.join(repr(v) for v in col.categories[:3])})" if len(col.categories) > 1 else None
                        })

            if not filterable:
                return json.dumps({
                    "success": True,
                    "message": "No filterable columns found" + (f" for table '{table_name}'" if table_name else ""),
                    "filterable_columns": []
                })

            # Group by table for easier reading
            by_table = {}
            for f in filterable:
                tbl = f["table"]
                if tbl not in by_table:
                    by_table[tbl] = []
                by_table[tbl].append({
                    "column": f["column"],
                    "type": f["data_type"],
                    "values": f["allowed_values"],
                    "cardinality": f["cardinality"]
                })

            return json.dumps({
                "success": True,
                "total_filterable_columns": len(filterable),
                "by_table": by_table,
                "all_columns": filterable,
                "usage_hint": "Use the exact values from 'allowed_values' in your WHERE clauses"
            }, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return get_filterable_columns


def create_search_tables_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool to search tables and columns using patterns."""
    from app.modules.table_description.repositories import TableDescriptionRepository

    table_repo = TableDescriptionRepository(storage)

    def search_tables(
        pattern: str,
        search_in: str = "all",
        case_sensitive: bool = False
    ) -> str:
        """Search for tables and columns matching a pattern.

        Supports wildcards like grep/glob:
        - '*' matches any characters (e.g., '*kpi*' matches 'sales_kpi', 'kpi_metrics')
        - '?' matches single character (e.g., 'user?' matches 'users', 'user1')
        - Use plain text for contains search (e.g., 'revenue' finds anything containing 'revenue')

        Args:
            pattern: Search pattern with optional wildcards (* or ?)
                     Examples: '*kpi*', 'user*', '*_id', 'revenue', 'order*item*'
            search_in: Where to search - 'tables', 'columns', 'descriptions', or 'all' (default)
            case_sensitive: Whether search is case-sensitive (default: False)

        Returns:
            JSON string with matching tables and columns, organized by match location
        """
        try:
            tables = table_repo.find_by({"db_connection_id": db_connection.id})

            if not tables:
                return json.dumps({
                    "success": False,
                    "error": "No tables found. Database may not be scanned yet."
                })

            # Convert pattern to regex
            # If pattern doesn't have wildcards, treat as contains search
            if '*' not in pattern and '?' not in pattern:
                regex_pattern = f".*{re.escape(pattern)}.*"
            else:
                # Convert glob-style wildcards to regex
                regex_pattern = fnmatch.translate(pattern)
                # fnmatch.translate adds \Z at end, we want to match anywhere
                regex_pattern = regex_pattern.replace(r'\Z', '')

            flags = 0 if case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(regex_pattern, flags)

            results = {
                "success": True,
                "pattern": pattern,
                "search_in": search_in,
                "matches": {
                    "tables": [],      # Tables where name matches
                    "columns": [],     # Columns where name matches
                    "descriptions": [] # Tables/columns where description matches
                },
                "summary": {
                    "total_matches": 0,
                    "tables_matched": 0,
                    "columns_matched": 0,
                    "descriptions_matched": 0
                }
            }

            for table in tables:
                table_full_name = f"{table.db_schema}.{table.table_name}"

                # Search in table names
                if search_in in ("all", "tables"):
                    if compiled_pattern.search(table.table_name):
                        results["matches"]["tables"].append({
                            "table": table_full_name,
                            "description": table.table_description,
                            "column_count": len(table.columns) if table.columns else 0
                        })
                        results["summary"]["tables_matched"] += 1

                # Search in table descriptions
                if search_in in ("all", "descriptions"):
                    if table.table_description and compiled_pattern.search(table.table_description):
                        # Avoid duplicates if table name also matched
                        already_matched = any(
                            m["table"] == table_full_name
                            for m in results["matches"]["tables"]
                        )
                        if not already_matched:
                            results["matches"]["descriptions"].append({
                                "type": "table",
                                "table": table_full_name,
                                "description": table.table_description,
                                "match_context": _extract_match_context(
                                    table.table_description, compiled_pattern
                                )
                            })
                            results["summary"]["descriptions_matched"] += 1

                # Search in columns
                if table.columns:
                    for col in table.columns:
                        # Search in column names
                        if search_in in ("all", "columns"):
                            if compiled_pattern.search(col.name):
                                results["matches"]["columns"].append({
                                    "table": table_full_name,
                                    "column": col.name,
                                    "type": col.data_type,
                                    "description": col.description,
                                    "is_primary_key": col.is_primary_key,
                                    "foreign_key": {
                                        "references": f"{col.foreign_key.reference_table}.{col.foreign_key.field_name}"
                                    } if col.foreign_key else None
                                })
                                results["summary"]["columns_matched"] += 1

                        # Search in column descriptions
                        if search_in in ("all", "descriptions"):
                            if col.description and compiled_pattern.search(col.description):
                                # Check if column name already matched
                                already_matched = any(
                                    m.get("column") == col.name and m.get("table") == table_full_name
                                    for m in results["matches"]["columns"]
                                )
                                if not already_matched:
                                    results["matches"]["descriptions"].append({
                                        "type": "column",
                                        "table": table_full_name,
                                        "column": col.name,
                                        "column_type": col.data_type,
                                        "description": col.description,
                                        "match_context": _extract_match_context(
                                            col.description, compiled_pattern
                                        )
                                    })
                                    results["summary"]["descriptions_matched"] += 1

            # Calculate total
            results["summary"]["total_matches"] = (
                results["summary"]["tables_matched"] +
                results["summary"]["columns_matched"] +
                results["summary"]["descriptions_matched"]
            )

            # Add helpful message if no matches
            if results["summary"]["total_matches"] == 0:
                results["message"] = f"No matches found for pattern '{pattern}'"
                results["suggestions"] = [
                    "Try a broader pattern (e.g., '*sale*' instead of 'sales_total')",
                    "Use 'all' for search_in to search everywhere",
                    "Check spelling or try partial matches"
                ]

            return json.dumps(results, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return search_tables


def _extract_match_context(text: str, pattern: re.Pattern, context_chars: int = 50) -> str:
    """Extract context around the first match in text."""
    match = pattern.search(text)
    if not match:
        return text[:100] + "..." if len(text) > 100 else text

    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)

    context = text[start:end]
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."

    return context
