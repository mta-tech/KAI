"""Business glossary tools for autonomous agent."""
import json

from app.modules.database_connection.models import DatabaseConnection
from app.data.db.storage import Storage


def create_get_business_glossary_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to get all business glossary entries.

    This tool allows the agent to load business terminology and metric definitions
    before running SQL queries or analysis.
    """
    from app.modules.business_glossary.repositories import BusinessGlossaryRepository

    glossary_repo = BusinessGlossaryRepository(storage)

    def get_business_glossary() -> str:
        """Get all business glossary entries for the current database connection.

        Business glossary entries define business metrics and their SQL calculations.
        Use this to understand business terminology before writing queries.

        Returns:
            JSON string with all glossary entries including:
            - metric: The business term (e.g., 'Revenue', 'MRR', 'Churn Rate')
            - alias: Alternative names for the metric
            - sql: The SQL query that calculates this metric
            - metadata: Additional context about the metric
        """
        try:
            glossaries = glossary_repo.find_by({"db_connection_id": db_connection.id})

            if not glossaries:
                return json.dumps({
                    "success": True,
                    "message": "No business glossary entries found for this database.",
                    "glossary": []
                })

            result = {
                "success": True,
                "glossary": [
                    {
                        "metric": g.metric,
                        "aliases": g.alias or [],
                        "sql": g.sql,
                        "metadata": g.metadata,
                    }
                    for g in glossaries
                ],
                "summary": {
                    "total_entries": len(glossaries),
                    "metrics": [g.metric for g in glossaries],
                }
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return get_business_glossary


def create_lookup_metric_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to look up a specific business metric by name or alias."""
    from app.modules.business_glossary.repositories import BusinessGlossaryRepository

    glossary_repo = BusinessGlossaryRepository(storage)

    def lookup_metric(metric_name: str) -> str:
        """Look up a specific business metric by name or alias.

        Use this when you encounter a business term in the user's question
        and need to understand how it's calculated.

        Args:
            metric_name: The metric name or alias to look up (e.g., 'Revenue', 'MRR')

        Returns:
            JSON string with the metric definition including its SQL calculation,
            or suggestions if no exact match is found.
        """
        try:
            glossaries = glossary_repo.find_by({"db_connection_id": db_connection.id})

            if not glossaries:
                return json.dumps({
                    "success": False,
                    "error": "No business glossary entries found for this database."
                })

            # Search for exact match on metric name or aliases
            metric_lower = metric_name.lower()
            matches = []

            for g in glossaries:
                # Check metric name
                if g.metric.lower() == metric_lower:
                    matches.append({
                        "metric": g.metric,
                        "aliases": g.alias or [],
                        "sql": g.sql,
                        "metadata": g.metadata,
                        "match_type": "exact"
                    })
                    continue

                # Check aliases
                if g.alias:
                    for alias in g.alias:
                        if alias.lower() == metric_lower:
                            matches.append({
                                "metric": g.metric,
                                "aliases": g.alias,
                                "sql": g.sql,
                                "metadata": g.metadata,
                                "match_type": "alias"
                            })
                            break

            if matches:
                return json.dumps({
                    "success": True,
                    "found": True,
                    "matches": matches
                }, indent=2, default=str)

            # No exact match - try partial matching
            partial_matches = []
            for g in glossaries:
                if metric_lower in g.metric.lower():
                    partial_matches.append(g.metric)
                elif g.alias:
                    for alias in g.alias:
                        if metric_lower in alias.lower():
                            partial_matches.append(g.metric)
                            break

            return json.dumps({
                "success": True,
                "found": False,
                "message": f"No exact match found for '{metric_name}'",
                "suggestions": partial_matches if partial_matches else None,
                "available_metrics": [g.metric for g in glossaries]
            }, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return lookup_metric


def create_search_metrics_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to search for metrics mentioned in a question."""
    from app.modules.business_glossary.repositories import BusinessGlossaryRepository

    glossary_repo = BusinessGlossaryRepository(storage)

    def search_metrics_in_question(question: str) -> str:
        """Search for business metrics mentioned in a user's question.

        Use this to automatically identify and retrieve relevant metric definitions
        from the user's natural language question.

        Args:
            question: The user's question or prompt to search for metrics

        Returns:
            JSON string with all metrics found in the question along with their
            SQL definitions.
        """
        try:
            # Use the repository's built-in full-text search
            matches = glossary_repo.find_by_metric(question)

            if not matches:
                # Fallback: check all glossaries for mentions
                glossaries = glossary_repo.find_by({"db_connection_id": db_connection.id})
                question_lower = question.lower()

                for g in glossaries:
                    if g.metric.lower() in question_lower:
                        matches.append({"metric": g.metric, "sql": g.sql})
                    elif g.alias:
                        for alias in g.alias:
                            if alias.lower() in question_lower:
                                matches.append({"metric": alias, "sql": g.sql})
                                break

            if matches:
                return json.dumps({
                    "success": True,
                    "found": True,
                    "metrics_found": matches,
                    "message": f"Found {len(matches)} metric(s) in the question. Use these SQL definitions as reference."
                }, indent=2, default=str)

            return json.dumps({
                "success": True,
                "found": False,
                "message": "No predefined business metrics found in the question."
            }, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return search_metrics_in_question
