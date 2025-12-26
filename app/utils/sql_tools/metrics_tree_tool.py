"""
MetricsTreeTool - LangGraph tool for querying business metrics graphs.

This tool enables AI agents to:
1. Query metric hierarchies and relationships
2. Get metric breakdowns for root cause analysis
3. Identify hot paths (biggest contributors to changes)
4. Answer "WHY" questions about metric changes
"""

import os
import httpx
from typing import Optional
from pydantic import Field

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool


# KC-Service URL for metrics graph API
KC_SERVICE_URL = os.getenv("KC_SERVICE_URL", "http://localhost:8001")


class MetricsTreeTool(BaseTool):
    """Tool for querying the business metrics graph for root cause analysis."""

    name: str = "MetricsTree"
    description: str = """
    Use this tool to analyze business metrics and their relationships.
    This helps answer "WHY" questions like "Why did revenue drop?" by showing
    which components contributed most to the change.

    Input: A JSON object with one of these actions:
    - {"action": "get_tree", "metric": "revenue", "depth": 3}
      Get the metric breakdown tree showing how a metric splits into components.

    - {"action": "get_hot_path", "metric": "revenue", "threshold": 0.2}
      Get the "hot path" - the chain of metrics with biggest contribution to variance.

    - {"action": "explain_change", "metric": "revenue", "change": "-15%", "breakdown": {...}}
      Get an AI explanation of why a metric changed based on its breakdown.

    - {"action": "list_metrics"}
      List all available metrics in the graph.

    Output: JSON with the requested metric data or explanation.
    """

    tenant_id: str = Field(description="Tenant ID for multi-tenancy isolation")
    http_client: Optional[httpx.Client] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, tenant_id: str, **kwargs):
        super().__init__(tenant_id=tenant_id, **kwargs)
        self.http_client = httpx.Client(
            base_url=KC_SERVICE_URL,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )

    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        """Execute the metrics tree query."""
        import json

        try:
            # Parse input
            if isinstance(query, str):
                try:
                    params = json.loads(query)
                except json.JSONDecodeError:
                    # If not JSON, treat as metric name for tree lookup
                    params = {"action": "get_tree", "metric": query}
            else:
                params = query

            action = params.get("action", "get_tree")

            if action == "get_tree":
                return self._get_metric_tree(
                    metric=params.get("metric", ""),
                    depth=params.get("depth", 3)
                )
            elif action == "get_hot_path":
                return self._get_hot_path(
                    metric=params.get("metric", ""),
                    threshold=params.get("threshold", 0.2)
                )
            elif action == "explain_change":
                return self._explain_change(
                    metric=params.get("metric", ""),
                    change=params.get("change", ""),
                    breakdown=params.get("breakdown", {})
                )
            elif action == "list_metrics":
                return self._list_metrics()
            else:
                return json.dumps({"error": f"Unknown action: {action}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def _get_metric_tree(self, metric: str, depth: int = 3) -> str:
        """Get the metric breakdown tree."""
        import json

        try:
            response = self.http_client.get(
                f"/api/v1/metrics-graph/tree/{metric}",
                params={"tenant_id": self.tenant_id, "depth": depth}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({
                "error": f"Failed to get metric tree: {e.response.status_code}",
                "message": str(e)
            })
        except Exception as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def _get_hot_path(self, metric: str, threshold: float = 0.2) -> str:
        """Get the hot path for a metric (biggest contributors)."""
        import json

        try:
            response = self.http_client.get(
                f"/api/v1/metrics-graph/hot-path/{metric}",
                params={"tenant_id": self.tenant_id, "threshold": threshold}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({
                "error": f"Failed to get hot path: {e.response.status_code}",
                "message": str(e)
            })
        except Exception as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def _explain_change(self, metric: str, change: str, breakdown: dict) -> str:
        """Get AI explanation for a metric change."""
        import json

        try:
            response = self.http_client.post(
                "/api/v1/metrics-graph/ai/explain",
                params={"tenant_id": self.tenant_id},
                json={
                    "metric_name": metric,
                    "change_description": change,
                    "breakdown_data": breakdown
                }
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({
                "error": f"Failed to get explanation: {e.response.status_code}",
                "message": str(e)
            })
        except Exception as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def _list_metrics(self) -> str:
        """List all metrics in the graph."""
        import json

        try:
            response = self.http_client.get(
                "/api/v1/metrics-graph/metrics",
                params={"tenant_id": self.tenant_id}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({
                "error": f"Failed to list metrics: {e.response.status_code}",
                "message": str(e)
            })
        except Exception as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})


class MetricsBreakdownTool(BaseTool):
    """Simplified tool focused on getting metric breakdowns."""

    name: str = "GetMetricBreakdown"
    description: str = """
    Get the breakdown of a business metric to understand its components.
    Use when a user asks "Why did X change?" or "How is X calculated?".

    Input: The metric name (e.g., "revenue", "orders", "conversion_rate")
    Output: The breakdown tree showing child metrics and their contributions.
    """

    tenant_id: str = Field(description="Tenant ID")
    http_client: Optional[httpx.Client] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, tenant_id: str, **kwargs):
        super().__init__(tenant_id=tenant_id, **kwargs)
        self.http_client = httpx.Client(
            base_url=KC_SERVICE_URL,
            timeout=30.0
        )

    def _run(
        self,
        metric_name: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        """Get the breakdown for a metric."""
        import json

        try:
            response = self.http_client.get(
                f"/api/v1/metrics-graph/tree/{metric_name.strip()}",
                params={"tenant_id": self.tenant_id, "depth": 2}
            )
            response.raise_for_status()
            data = response.json()

            # Format for readability
            if "nodes" in data and "edges" in data:
                formatted = self._format_tree(data)
                return formatted
            return json.dumps(data, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Could not get breakdown for '{metric_name}': {str(e)}"})

    def _format_tree(self, data: dict) -> str:
        """Format the tree data for human readability."""
        nodes = {n["id"]: n for n in data.get("nodes", [])}
        edges = data.get("edges", [])

        # Build tree structure
        lines = []
        root_id = data.get("root_id")
        if root_id and root_id in nodes:
            root = nodes[root_id]
            lines.append(f"📊 {root.get('display_name', root_id)}")

            # Find children
            for edge in edges:
                if edge.get("source") == root_id:
                    child_id = edge.get("target")
                    if child_id in nodes:
                        child = nodes[child_id]
                        contribution = edge.get("properties", {}).get("contribution_weight")
                        contrib_str = f" ({contribution*100:.1f}%)" if contribution else ""
                        lines.append(f"  └─ {child.get('display_name', child_id)}{contrib_str}")

        return "\n".join(lines) if lines else "No breakdown found"


def create_metrics_tools(tenant_id: str) -> list[BaseTool]:
    """Factory function to create metrics tools for a tenant."""
    return [
        MetricsTreeTool(tenant_id=tenant_id),
        MetricsBreakdownTool(tenant_id=tenant_id),
    ]
