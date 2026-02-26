"""MDL manifest explorer tools for the autonomous agent.

These tools allow the agent to explore and understand the MDL semantic layer
manifest, including models, relationships, metrics, and views.
"""

from __future__ import annotations

import asyncio
import json
import logging

logger = logging.getLogger(__name__)


def create_get_mdl_manifest_tool(db_connection_id: str, storage):
    """Create a tool to get the MDL manifest for a database connection.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Get manifest function.
    """

    def get_mdl_manifest() -> str:
        """Get the MDL semantic layer manifest for this database.

        Use this tool to understand the semantic layer structure including:
        - Available models (tables) and their columns
        - Relationships between models
        - Business metrics definitions
        - Saved views

        Returns:
            JSON with manifest overview or not found message.

        Example:
            result = get_mdl_manifest()
            # Returns: {"found": true, "name": "Sales Analytics", "models": [...], ...}
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            # Run async method synchronously
            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "message": "No MDL manifest found for this database connection",
                    "recommendation": "Create an MDL manifest using the API or build_mdl_manifest tool",
                })

            # Return overview without full details
            return json.dumps({
                "found": True,
                "manifest_id": manifest.id,
                "name": manifest.name,
                "catalog": manifest.catalog,
                "schema": manifest.schema_name,
                "data_source": manifest.data_source,
                "summary": {
                    "total_models": len(manifest.models),
                    "total_relationships": len(manifest.relationships),
                    "total_metrics": len(manifest.metrics),
                    "total_views": len(manifest.views),
                },
                "models": [m.name for m in manifest.models],
                "relationships": [r.name for r in manifest.relationships],
                "metrics": [m.name for m in manifest.metrics],
                "views": [v.name for v in manifest.views],
                "created_at": manifest.created_at,
                "updated_at": manifest.updated_at,
            })

        except Exception as e:
            logger.error(f"Error getting MDL manifest: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return get_mdl_manifest


def create_explore_mdl_model_tool(db_connection_id: str, storage):
    """Create a tool to explore a specific model in the MDL manifest.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Explore model function.
    """

    def explore_mdl_model(model_name: str) -> str:
        """Explore a specific model (table) in the MDL manifest.

        Use this tool to get detailed information about a model including:
        - All columns with types and properties
        - Primary key
        - Calculated columns and expressions
        - Related relationships

        Args:
            model_name: Name of the model to explore.

        Returns:
            JSON with model details or not found message.

        Example:
            result = explore_mdl_model("sales")
            # Returns full column details, relationships, etc.
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            # Find the model
            model = next((m for m in manifest.models if m.name.lower() == model_name.lower()), None)
            if not model:
                available = [m.name for m in manifest.models]
                return json.dumps({
                    "found": False,
                    "error": f"Model '{model_name}' not found",
                    "available_models": available,
                    "suggestion": f"Did you mean one of: {', '.join(available[:5])}?" if available else None,
                })

            # Find related relationships
            related_relationships = [
                {
                    "name": r.name,
                    "models": r.models,
                    "join_type": r.join_type.value,
                    "condition": r.condition,
                }
                for r in manifest.relationships
                if model_name.lower() in [m.lower() for m in r.models]
            ]

            # Build column details
            columns = []
            for col in model.columns:
                col_info = {
                    "name": col.name,
                    "type": col.type,
                }
                if col.not_null:
                    col_info["not_null"] = True
                if col.is_calculated:
                    col_info["is_calculated"] = True
                    col_info["expression"] = col.expression
                if col.relationship:
                    col_info["relationship"] = col.relationship
                if col.is_hidden:
                    col_info["is_hidden"] = True
                if col.properties:
                    col_info["properties"] = col.properties
                columns.append(col_info)

            return json.dumps({
                "found": True,
                "model": {
                    "name": model.name,
                    "table_reference": model.table_reference,
                    "ref_sql": model.ref_sql,
                    "primary_key": model.primary_key,
                    "cached": model.cached,
                    "refresh_time": model.refresh_time,
                    "properties": model.properties,
                    "column_count": len(columns),
                    "columns": columns,
                },
                "relationships": related_relationships,
                "relationship_count": len(related_relationships),
            })

        except Exception as e:
            logger.error(f"Error exploring MDL model: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return explore_mdl_model


def create_explore_mdl_relationships_tool(db_connection_id: str, storage):
    """Create a tool to explore relationships in the MDL manifest.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Explore relationships function.
    """

    def explore_mdl_relationships(model_name: str | None = None) -> str:
        """Explore relationships between models in the MDL manifest.

        Use this tool to understand how models are connected:
        - Join types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY)
        - Join conditions
        - Related models

        Args:
            model_name: Optional - filter relationships involving this model.
                       If not provided, returns all relationships.

        Returns:
            JSON with relationship details.

        Example:
            result = explore_mdl_relationships("orders")
            # Returns relationships involving the orders model
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            relationships = manifest.relationships

            # Filter by model if specified
            if model_name:
                relationships = [
                    r for r in relationships
                    if model_name.lower() in [m.lower() for m in r.models]
                ]

                if not relationships:
                    return json.dumps({
                        "found": True,
                        "model_filter": model_name,
                        "relationships": [],
                        "message": f"No relationships found involving model '{model_name}'",
                        "available_models": [m.name for m in manifest.models],
                    })

            # Format relationships
            rel_list = [
                {
                    "name": r.name,
                    "from_model": r.models[0] if r.models else None,
                    "to_model": r.models[1] if len(r.models) > 1 else None,
                    "join_type": r.join_type.value,
                    "condition": r.condition,
                    "properties": r.properties,
                }
                for r in relationships
            ]

            # Build relationship graph summary
            graph = {}
            for r in relationships:
                if len(r.models) >= 2:
                    from_m, to_m = r.models[0], r.models[1]
                    if from_m not in graph:
                        graph[from_m] = []
                    graph[from_m].append({
                        "to": to_m,
                        "type": r.join_type.value,
                        "via": r.name,
                    })

            return json.dumps({
                "found": True,
                "model_filter": model_name,
                "total_relationships": len(rel_list),
                "relationships": rel_list,
                "graph": graph,
            })

        except Exception as e:
            logger.error(f"Error exploring MDL relationships: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return explore_mdl_relationships


def create_explore_mdl_metrics_tool(db_connection_id: str, storage):
    """Create a tool to explore metrics in the MDL manifest.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Explore metrics function.
    """

    def explore_mdl_metrics(metric_name: str | None = None) -> str:
        """Explore business metrics defined in the MDL manifest.

        Use this tool to understand pre-defined business metrics:
        - Metric definitions and base objects
        - Dimensions for grouping
        - Measures (aggregations)
        - Time grain options

        Args:
            metric_name: Optional - get details for a specific metric.
                        If not provided, returns all metrics summary.

        Returns:
            JSON with metric details.

        Example:
            result = explore_mdl_metrics("revenue")
            # Returns full details of the revenue metric
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            if not manifest.metrics:
                return json.dumps({
                    "found": True,
                    "metrics": [],
                    "message": "No metrics defined in the MDL manifest",
                    "recommendation": "Define metrics using the MDL API for reusable business calculations",
                })

            # If specific metric requested
            if metric_name:
                metric = next(
                    (m for m in manifest.metrics if m.name.lower() == metric_name.lower()),
                    None
                )
                if not metric:
                    return json.dumps({
                        "found": False,
                        "error": f"Metric '{metric_name}' not found",
                        "available_metrics": [m.name for m in manifest.metrics],
                    })

                return json.dumps({
                    "found": True,
                    "metric": {
                        "name": metric.name,
                        "base_object": metric.base_object,
                        "dimensions": [
                            {"name": d.name, "type": d.type, "expression": d.expression}
                            for d in (metric.dimension or [])
                        ],
                        "measures": [
                            {
                                "name": m.name,
                                "type": m.type,
                                "expression": m.expression,
                                "is_calculated": m.is_calculated,
                            }
                            for m in (metric.measure or [])
                        ],
                        "time_grains": [
                            {
                                "name": t.name,
                                "ref_column": t.ref_column,
                                "date_parts": [dp.value for dp in t.date_parts],
                            }
                            for t in (metric.time_grain or [])
                        ],
                        "cached": metric.cached,
                        "refresh_time": metric.refresh_time,
                        "properties": metric.properties,
                    },
                })

            # Return all metrics summary
            metrics_summary = [
                {
                    "name": m.name,
                    "base_object": m.base_object,
                    "dimension_count": len(m.dimension or []),
                    "measure_count": len(m.measure or []),
                    "time_grain_count": len(m.time_grain or []),
                    "cached": m.cached,
                }
                for m in manifest.metrics
            ]

            return json.dumps({
                "found": True,
                "total_metrics": len(metrics_summary),
                "metrics": metrics_summary,
                "tip": "Use explore_mdl_metrics('metric_name') for full details",
            })

        except Exception as e:
            logger.error(f"Error exploring MDL metrics: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return explore_mdl_metrics


def create_explore_mdl_views_tool(db_connection_id: str, storage):
    """Create a tool to explore views in the MDL manifest.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Explore views function.
    """

    def explore_mdl_views(view_name: str | None = None) -> str:
        """Explore saved views in the MDL manifest.

        Use this tool to see pre-defined SQL views:
        - View names and statements
        - Reusable query definitions

        Args:
            view_name: Optional - get details for a specific view.
                      If not provided, returns all views.

        Returns:
            JSON with view details.

        Example:
            result = explore_mdl_views("monthly_sales")
            # Returns the SQL statement for monthly_sales view
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            if not manifest.views:
                return json.dumps({
                    "found": True,
                    "views": [],
                    "message": "No views defined in the MDL manifest",
                })

            # If specific view requested
            if view_name:
                view = next(
                    (v for v in manifest.views if v.name.lower() == view_name.lower()),
                    None
                )
                if not view:
                    return json.dumps({
                        "found": False,
                        "error": f"View '{view_name}' not found",
                        "available_views": [v.name for v in manifest.views],
                    })

                return json.dumps({
                    "found": True,
                    "view": {
                        "name": view.name,
                        "statement": view.statement,
                        "properties": view.properties,
                    },
                })

            # Return all views
            views_list = [
                {
                    "name": v.name,
                    "statement_preview": v.statement[:200] + "..." if len(v.statement) > 200 else v.statement,
                    "properties": v.properties,
                }
                for v in manifest.views
            ]

            return json.dumps({
                "found": True,
                "total_views": len(views_list),
                "views": views_list,
            })

        except Exception as e:
            logger.error(f"Error exploring MDL views: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return explore_mdl_views


def create_search_mdl_columns_tool(db_connection_id: str, storage):
    """Create a tool to search columns across all models.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Search columns function.
    """

    def search_mdl_columns(search_term: str, column_type: str | None = None) -> str:
        """Search for columns across all models in the MDL manifest.

        Use this tool to find columns by name or type:
        - Find all date columns for time-based analysis
        - Find amount/price columns for financial analysis
        - Find ID columns for joining

        Args:
            search_term: Term to search in column names (case-insensitive).
            column_type: Optional - filter by column type (e.g., 'INTEGER', 'VARCHAR').

        Returns:
            JSON with matching columns and their locations.

        Example:
            result = search_mdl_columns("amount")
            # Returns all columns containing "amount" in their name
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            search_lower = search_term.lower()
            type_filter = column_type.upper() if column_type else None

            matches = []
            for model in manifest.models:
                for col in model.columns:
                    name_match = search_lower in col.name.lower()
                    type_match = (not type_filter) or (type_filter in col.type.upper())

                    if name_match and type_match:
                        match_info = {
                            "model": model.name,
                            "column": col.name,
                            "type": col.type,
                            "full_path": f"{model.name}.{col.name}",
                        }
                        if col.is_calculated:
                            match_info["is_calculated"] = True
                            match_info["expression"] = col.expression
                        if col.properties and col.properties.get("description"):
                            match_info["description"] = col.properties["description"]
                        matches.append(match_info)

            if not matches:
                return json.dumps({
                    "found": True,
                    "search_term": search_term,
                    "type_filter": column_type,
                    "matches": [],
                    "message": f"No columns matching '{search_term}' found",
                })

            return json.dumps({
                "found": True,
                "search_term": search_term,
                "type_filter": column_type,
                "total_matches": len(matches),
                "matches": matches,
            })

        except Exception as e:
            logger.error(f"Error searching MDL columns: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return search_mdl_columns


def create_get_mdl_join_path_tool(db_connection_id: str, storage):
    """Create a tool to find join paths between models.

    Args:
        db_connection_id: Database connection ID.
        storage: Storage instance.

    Returns:
        Get join path function.
    """

    def get_mdl_join_path(from_model: str, to_model: str) -> str:
        """Find the join path between two models in the MDL manifest.

        Use this tool to understand how to join tables:
        - Direct relationships
        - Join conditions to use
        - Intermediate tables if needed

        Args:
            from_model: Starting model name.
            to_model: Target model name.

        Returns:
            JSON with join path details.

        Example:
            result = get_mdl_join_path("orders", "customers")
            # Returns the relationship and join condition
        """
        try:
            from app.modules.mdl.repositories import MDLRepository

            repo = MDLRepository(storage)

            loop = asyncio.new_event_loop()
            try:
                manifest = loop.run_until_complete(
                    repo.get_by_db_connection(db_connection_id)
                )
            finally:
                loop.close()

            if not manifest:
                return json.dumps({
                    "found": False,
                    "error": "No MDL manifest found for this database",
                })

            from_lower = from_model.lower()
            to_lower = to_model.lower()

            # Check if models exist
            model_names = {m.name.lower(): m.name for m in manifest.models}
            if from_lower not in model_names:
                return json.dumps({
                    "found": False,
                    "error": f"Model '{from_model}' not found",
                    "available_models": list(model_names.values()),
                })
            if to_lower not in model_names:
                return json.dumps({
                    "found": False,
                    "error": f"Model '{to_model}' not found",
                    "available_models": list(model_names.values()),
                })

            # Find direct relationship
            direct_rel = None
            for r in manifest.relationships:
                models_lower = [m.lower() for m in r.models]
                if from_lower in models_lower and to_lower in models_lower:
                    direct_rel = r
                    break

            if direct_rel:
                return json.dumps({
                    "found": True,
                    "path_type": "direct",
                    "from_model": model_names[from_lower],
                    "to_model": model_names[to_lower],
                    "relationship": {
                        "name": direct_rel.name,
                        "join_type": direct_rel.join_type.value,
                        "condition": direct_rel.condition,
                    },
                    "sql_hint": f"JOIN {model_names[to_lower]} ON {direct_rel.condition}",
                })

            # Try to find indirect path (1 hop)
            from_connections = {}
            to_connections = {}

            for r in manifest.relationships:
                models_lower = [m.lower() for m in r.models]
                if from_lower in models_lower:
                    other = [m for m in models_lower if m != from_lower][0] if len(models_lower) > 1 else None
                    if other:
                        from_connections[other] = r
                if to_lower in models_lower:
                    other = [m for m in models_lower if m != to_lower][0] if len(models_lower) > 1 else None
                    if other:
                        to_connections[other] = r

            # Find common intermediate model
            intermediate = set(from_connections.keys()) & set(to_connections.keys())
            if intermediate:
                via = list(intermediate)[0]
                return json.dumps({
                    "found": True,
                    "path_type": "indirect",
                    "from_model": model_names[from_lower],
                    "to_model": model_names[to_lower],
                    "via_model": model_names.get(via, via),
                    "relationships": [
                        {
                            "step": 1,
                            "name": from_connections[via].name,
                            "join_type": from_connections[via].join_type.value,
                            "condition": from_connections[via].condition,
                        },
                        {
                            "step": 2,
                            "name": to_connections[via].name,
                            "join_type": to_connections[via].join_type.value,
                            "condition": to_connections[via].condition,
                        },
                    ],
                })

            return json.dumps({
                "found": False,
                "from_model": model_names[from_lower],
                "to_model": model_names[to_lower],
                "message": f"No relationship path found between '{from_model}' and '{to_model}'",
                "from_connected_to": list(from_connections.keys()),
                "to_connected_to": list(to_connections.keys()),
            })

        except Exception as e:
            logger.error(f"Error getting MDL join path: {e}")
            return json.dumps({
                "found": False,
                "error": str(e),
            })

    return get_mdl_join_path
