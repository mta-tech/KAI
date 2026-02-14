"""Notebook generation and execution tools for the autonomous agent."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Literal

from app.data.db.storage import Storage
from app.modules.notebook.models import (
    Cell,
    CellType,
    Notebook,
    NotebookCreateRequest,
    Parameter,
)
from app.modules.notebook.services import NotebookService


def create_notebook_tool(storage: Storage, output_dir: str | None = None):
    """Create a notebook creation tool.

    Args:
        storage: Storage instance for persisting notebooks.
        output_dir: Optional directory to save notebook exports.

    Returns:
        Notebook creation function.
    """

    def create_notebook(
        name: str,
        description: str,
        cells_json: str,
        parameters_json: str | None = None,
        database_alias: str | None = None,
        tags: str | None = None,
    ) -> str:
        """Create a reusable analysis notebook with cells and parameters.

        Notebooks are structured workflows that can be rerun with different parameters.
        Each cell can be a query, visualization, text, code, or user_input type.

        Args:
            name: Notebook name (e.g., "Monthly Sales Report").
            description: Brief description of what the notebook does.
            cells_json: JSON array of cells. Each cell should have:
                - id: Unique cell identifier
                - name: Cell name (used for references)
                - cell_type: One of "query", "visualization", "text", "code", "user_input"
                - prompt: The prompt/content for the cell (use {{param}} for parameters)
                - depends_on: Array of cell names this cell depends on
            parameters_json: Optional JSON array of parameters. Each parameter has:
                - name: Parameter name (referenced as {{name}} in cells)
                - param_type: "text", "date", "number", "select"
                - default: Default value
                - description: Parameter description
                - required: Whether parameter is required
            database_alias: Database to use for queries.
            tags: Comma-separated tags for categorization.

        Returns:
            JSON string with created notebook details.

        Example:
            cells_json = '[
                {"id": "1", "name": "sales_query", "cell_type": "query",
                 "prompt": "Get total sales for {{month}}"},
                {"id": "2", "name": "sales_chart", "cell_type": "visualization",
                 "prompt": "Create bar chart of sales", "depends_on": ["sales_query"]}
            ]'
            parameters_json = '[
                {"name": "month", "param_type": "text", "default": "January"}
            ]'
        """
        try:
            # Parse cells
            cells_data = json.loads(cells_json)
            cells = []
            for i, cell_data in enumerate(cells_data):
                cell = Cell(
                    id=cell_data.get("id", f"cell_{i}"),
                    name=cell_data.get("name", f"Cell {i+1}"),
                    cell_type=CellType(cell_data.get("cell_type", "text")),
                    prompt=cell_data.get("prompt"),
                    code=cell_data.get("code"),
                    depends_on=cell_data.get("depends_on", []),
                )
                cells.append(cell)

            # Parse parameters
            parameters = []
            if parameters_json:
                params_data = json.loads(parameters_json)
                for param_data in params_data:
                    param = Parameter(
                        name=param_data.get("name"),
                        param_type=param_data.get("param_type", "text"),
                        default=param_data.get("default"),
                        description=param_data.get("description"),
                        options=param_data.get("options"),
                        required=param_data.get("required", False),
                    )
                    parameters.append(param)

            # Parse tags
            tag_list = []
            if tags:
                tag_list = [t.strip() for t in tags.split(",")]

            # Create notebook
            request = NotebookCreateRequest(
                name=name,
                description=description,
                database_alias=database_alias,
                parameters=parameters,
                cells=cells,
                tags=tag_list,
            )

            service = NotebookService(storage)
            notebook = service.create_notebook(request)

            # Export to file if output_dir is specified
            export_path = None
            if output_dir:
                export_path = os.path.join(
                    output_dir, f"notebook_{notebook.id[:8]}.json"
                )
                Path(export_path).parent.mkdir(parents=True, exist_ok=True)
                with open(export_path, "w") as f:
                    json.dump(notebook.model_dump(mode="json"), f, indent=2, default=str)

            return json.dumps({
                "success": True,
                "notebook_id": notebook.id,
                "name": notebook.name,
                "cells_count": len(notebook.cells),
                "parameters_count": len(notebook.parameters),
                "tags": notebook.tags,
                "exported_to": export_path,
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return create_notebook


def create_list_notebooks_tool(storage: Storage):
    """Create a tool to list available notebooks.

    Args:
        storage: Storage instance.

    Returns:
        List notebooks function.
    """

    def list_notebooks(tags: str | None = None, limit: int = 20) -> str:
        """List available notebooks with optional tag filter.

        Args:
            tags: Optional comma-separated tags to filter by.
            limit: Maximum number of notebooks to return.

        Returns:
            JSON string with list of notebooks.
        """
        try:
            service = NotebookService(storage)

            tag_list = None
            if tags:
                tag_list = [t.strip() for t in tags.split(",")]

            notebooks = service.list_notebooks(tags=tag_list, limit=limit)

            return json.dumps({
                "success": True,
                "count": len(notebooks),
                "notebooks": [
                    {
                        "id": nb.id,
                        "name": nb.name,
                        "description": nb.description,
                        "cells_count": len(nb.cells),
                        "tags": nb.tags,
                        "created_at": nb.created_at.isoformat(),
                    }
                    for nb in notebooks
                ],
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return list_notebooks


def create_get_notebook_tool(storage: Storage):
    """Create a tool to get notebook details.

    Args:
        storage: Storage instance.

    Returns:
        Get notebook function.
    """

    def get_notebook(notebook_id: str) -> str:
        """Get details of a specific notebook.

        Args:
            notebook_id: The notebook ID.

        Returns:
            JSON string with notebook details and cells.
        """
        try:
            service = NotebookService(storage)
            notebook = service.get_notebook(notebook_id)

            if not notebook:
                return json.dumps({
                    "success": False,
                    "error": f"Notebook '{notebook_id}' not found",
                })

            return json.dumps({
                "success": True,
                "notebook": {
                    "id": notebook.id,
                    "name": notebook.name,
                    "description": notebook.description,
                    "database_alias": notebook.database_alias,
                    "parameters": [p.model_dump() for p in notebook.parameters],
                    "cells": [
                        {
                            "id": c.id,
                            "name": c.name,
                            "cell_type": c.cell_type.value,
                            "prompt": c.prompt,
                            "depends_on": c.depends_on,
                        }
                        for c in notebook.cells
                    ],
                    "tags": notebook.tags,
                    "created_at": notebook.created_at.isoformat(),
                },
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return get_notebook


def create_export_notebook_tool(storage: Storage, output_dir: str):
    """Create a tool to export notebooks to different formats.

    Args:
        storage: Storage instance.
        output_dir: Directory to save exports.

    Returns:
        Export notebook function.
    """

    def export_notebook(
        notebook_id: str,
        format: Literal["json", "jupyter", "markdown"] = "json",
    ) -> str:
        """Export a notebook to different formats.

        Args:
            notebook_id: The notebook ID to export.
            format: Export format - "json", "jupyter" (.ipynb), or "markdown".

        Returns:
            JSON string with export path.
        """
        try:
            service = NotebookService(storage)
            notebook = service.get_notebook(notebook_id)

            if not notebook:
                return json.dumps({
                    "success": False,
                    "error": f"Notebook '{notebook_id}' not found",
                })

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            if format == "json":
                filename = f"{notebook.name.replace(' ', '_').lower()}_{notebook.id[:8]}.json"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w") as f:
                    json.dump(notebook.model_dump(mode="json"), f, indent=2, default=str)

            elif format == "jupyter":
                filename = f"{notebook.name.replace(' ', '_').lower()}_{notebook.id[:8]}.ipynb"
                filepath = os.path.join(output_dir, filename)
                jupyter_nb = _to_jupyter(notebook)
                with open(filepath, "w") as f:
                    json.dump(jupyter_nb, f, indent=2)

            elif format == "markdown":
                filename = f"{notebook.name.replace(' ', '_').lower()}_{notebook.id[:8]}.md"
                filepath = os.path.join(output_dir, filename)
                markdown = _to_markdown(notebook)
                with open(filepath, "w") as f:
                    f.write(markdown)

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown format: {format}",
                })

            return json.dumps({
                "success": True,
                "notebook_id": notebook.id,
                "name": notebook.name,
                "format": format,
                "exported_to": filepath,
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    return export_notebook


def _to_jupyter(notebook: Notebook) -> dict:
    """Convert KAI notebook to Jupyter notebook format."""
    cells = []

    # Add title cell
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            f"# {notebook.name}\n",
            f"\n{notebook.description or ''}\n",
            f"\nCreated: {notebook.created_at.isoformat()}\n",
        ],
    })

    # Add parameters cell if any
    if notebook.parameters:
        params_code = "# Parameters\n"
        for param in notebook.parameters:
            default = repr(param.default) if param.default is not None else "''"
            params_code += f"{param.name} = {default}  # {param.description or param.param_type}\n"

        cells.append({
            "cell_type": "code",
            "metadata": {},
            "source": [params_code],
            "outputs": [],
            "execution_count": None,
        })

    # Add notebook cells
    for cell in notebook.cells:
        if cell.cell_type == CellType.TEXT:
            cells.append({
                "cell_type": "markdown",
                "metadata": {"kai_cell_id": cell.id, "kai_cell_name": cell.name},
                "source": [f"## {cell.name}\n\n{cell.prompt or ''}"],
            })
        elif cell.cell_type == CellType.QUERY:
            cells.append({
                "cell_type": "code",
                "metadata": {"kai_cell_id": cell.id, "kai_cell_name": cell.name},
                "source": [
                    f"# {cell.name}\n",
                    f"# Query: {cell.prompt or ''}\n",
                    "# TODO: Execute query via KAI\n",
                    f"# Depends on: {cell.depends_on}\n",
                ],
                "outputs": [],
                "execution_count": None,
            })
        elif cell.cell_type == CellType.VISUALIZATION:
            cells.append({
                "cell_type": "code",
                "metadata": {"kai_cell_id": cell.id, "kai_cell_name": cell.name},
                "source": [
                    f"# {cell.name}\n",
                    f"# Visualization: {cell.prompt or ''}\n",
                    "# TODO: Generate chart via KAI\n",
                    f"# Data from: {cell.depends_on}\n",
                ],
                "outputs": [],
                "execution_count": None,
            })
        elif cell.cell_type == CellType.CODE:
            cells.append({
                "cell_type": "code",
                "metadata": {"kai_cell_id": cell.id, "kai_cell_name": cell.name},
                "source": [cell.code or "# Code cell\n"],
                "outputs": [],
                "execution_count": None,
            })

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "kai_notebook_id": notebook.id,
            "kai_database_alias": notebook.database_alias,
        },
        "cells": cells,
    }


def _to_markdown(notebook: Notebook) -> str:
    """Convert KAI notebook to Markdown format."""
    lines = [
        f"# {notebook.name}\n",
        f"\n{notebook.description or ''}\n",
        f"\n**Created:** {notebook.created_at.isoformat()}\n",
        f"**Database:** {notebook.database_alias or 'Not specified'}\n",
    ]

    if notebook.tags:
        lines.append(f"**Tags:** {', '.join(notebook.tags)}\n")

    if notebook.parameters:
        lines.append("\n## Parameters\n")
        for param in notebook.parameters:
            required = " (required)" if param.required else ""
            default = f" = `{param.default}`" if param.default else ""
            lines.append(f"- **{param.name}**{required}{default}: {param.description or param.param_type}\n")

    lines.append("\n## Workflow\n")

    for i, cell in enumerate(notebook.cells, 1):
        lines.append(f"\n### Step {i}: {cell.name}\n")
        lines.append(f"**Type:** {cell.cell_type.value}\n")

        if cell.depends_on:
            lines.append(f"**Depends on:** {', '.join(cell.depends_on)}\n")

        if cell.prompt:
            lines.append(f"\n{cell.prompt}\n")

        if cell.code:
            lines.append(f"\n```python\n{cell.code}\n```\n")

    return "".join(lines)


# ============================================================================
# Artifact Generation Helpers
# ============================================================================

from app.modules.autonomous_agent.models.artifact import (
    ArtifactProvenance,
    ArtifactType,
    MissionArtifact,
    NotebookArtifact,
    SummaryArtifact,
    VerifiedSQLArtifact,
)


def create_notebook_artifact(
    notebook: Notebook,
    mission_id: str,
    source_asset_ids: list[str] | None = None,
    analysis_type: str | None = None,
    generated_by: str | None = None,
    confidence: float = 0.0,
) -> NotebookArtifact:
    """Create a notebook artifact from a notebook.

    Args:
        notebook: The notebook to create an artifact for.
        mission_id: ID of the mission that produced this artifact.
        source_asset_ids: List of context asset IDs that contributed.
        analysis_type: Type of analysis (e.g., "timeseries", "comparison").
        generated_by: Agent or service that created the artifact.
        confidence: Confidence in artifact quality (0-1).

    Returns:
        NotebookArtifact with provenance information.
    """
    provenance = ArtifactProvenance(
        source_asset_ids=source_asset_ids or [],
        source_asset_types=[],
        mission_id=mission_id,
        mission_stage="execute",
        generated_by=generated_by,
        confidence=confidence,
    )

    return NotebookArtifact(
        id=f"nb_artifact_{uuid.uuid4().hex[:12]}",
        mission_id=mission_id,
        name=notebook.name,
        description=notebook.description,
        notebook_id=notebook.id,
        cell_count=len(notebook.cells),
        parameter_count=len(notebook.parameters),
        analysis_type=analysis_type,
        database_alias=notebook.database_alias,
        provenance=provenance,
        content={
            "notebook_id": notebook.id,
            "name": notebook.name,
            "description": notebook.description,
            "database_alias": notebook.database_alias,
            "tags": notebook.tags,
        },
    )


def create_verified_sql_artifact(
    sql_query: str,
    mission_id: str,
    source_asset_ids: list[str] | None = None,
    is_validated: bool = False,
    validation_errors: list[str] | None = None,
    generated_by: str | None = None,
    confidence: float = 0.0,
    row_count_estimate: int | None = None,
) -> VerifiedSQLArtifact:
    """Create a verified SQL artifact.

    Args:
        sql_query: The SQL query to create an artifact for.
        mission_id: ID of the mission that produced this artifact.
        source_asset_ids: List of context asset IDs that contributed.
        is_validated: Whether the query has been validated.
        validation_errors: List of validation errors (if any).
        generated_by: Agent or service that created the artifact.
        confidence: Confidence in query quality (0-1).
        row_count_estimate: Estimated number of rows returned.

    Returns:
        VerifiedSQLArtifact with provenance information.
    """
    import hashlib

    query_hash = hashlib.md5(sql_query.encode()).hexdigest()[:16]

    provenance = ArtifactProvenance(
        source_asset_ids=source_asset_ids or [],
        source_asset_types=[],
        mission_id=mission_id,
        mission_stage="execute",
        generated_by=generated_by,
        confidence=confidence,
    )

    artifact = VerifiedSQLArtifact(
        id=f"sql_artifact_{uuid.uuid4().hex[:12]}",
        mission_id=mission_id,
        name=f"SQL Query {query_hash[:8]}",
        description=f"Verified SQL query from mission {mission_id[:8]}",
        sql_query=sql_query,
        is_validated=is_validated,
        validation_errors=validation_errors or [],
        row_count_estimate=row_count_estimate,
        provenance=provenance,
        content={
            "sql_query": sql_query,
            "query_hash": query_hash,
            "is_validated": is_validated,
        },
    )
    # query_hash is auto-generated in __post_init__, but we set it here for consistency
    artifact.query_hash = query_hash
    return artifact


def create_summary_artifact(
    question: str,
    answer: str,
    mission_id: str,
    key_findings: list[str] | None = None,
    methodology: str | None = None,
    linked_artifact_ids: list[str] | None = None,
    sql_queries_used: list[str] | None = None,
    source_asset_ids: list[str] | None = None,
    suggested_questions: list[str] | None = None,
    generated_by: str | None = None,
    confidence: float = 0.0,
    completeness: float = 0.0,
) -> SummaryArtifact:
    """Create a summary artifact for a mission.

    Args:
        question: The original question asked.
        answer: The answer produced by the mission.
        mission_id: ID of the mission.
        key_findings: List of key findings from the analysis.
        methodology: Description of the methodology used.
        linked_artifact_ids: IDs of other artifacts produced.
        sql_queries_used: List of SQL queries executed.
        source_asset_ids: List of context asset IDs that contributed.
        suggested_questions: List of suggested follow-up questions.
        generated_by: Agent or service that created the artifact.
        confidence: Confidence in answer quality (0-1).
        completeness: How completely the question was answered (0-1).

    Returns:
        SummaryArtifact with provenance information.
    """
    provenance = ArtifactProvenance(
        source_asset_ids=source_asset_ids or [],
        source_asset_types=[],
        mission_id=mission_id,
        mission_stage="synthesize",
        generated_by=generated_by,
        confidence=confidence,
    )

    return SummaryArtifact(
        id=f"summary_artifact_{uuid.uuid4().hex[:12]}",
        mission_id=mission_id,
        name=f"Summary: {question[:50]}...",
        description=f"Mission summary for {mission_id[:8]}",
        question=question,
        answer=answer,
        key_findings=key_findings or [],
        methodology=methodology,
        linked_artifact_ids=linked_artifact_ids or [],
        sql_queries_used=sql_queries_used or [],
        suggested_questions=suggested_questions or [],
        confidence_score=confidence,
        completeness_score=completeness,
        provenance=provenance,
        tags=["summary", "mission"],
        content={
            "question": question,
            "answer": answer,
            "key_findings": key_findings or [],
            "methodology": methodology,
        },
    )


def link_artifact_to_mission(
    artifact: MissionArtifact,
    mission_id: str,
) -> dict:
    """Format an artifact for linking to a mission run.

    Args:
        artifact: The artifact to link.
        mission_id: ID of the mission to link to.

    Returns:
        Dictionary format for storing in mission artifacts list.
    """
    return {
        "artifact_id": artifact.id,
        "artifact_type": artifact.artifact_type.value,
        "name": artifact.name,
        "description": artifact.description,
        "created_at": artifact.created_at,
        "provenance": {
            "mission_id": artifact.provenance.mission_id,
            "source_asset_ids": artifact.provenance.source_asset_ids,
            "generated_by": artifact.provenance.generated_by,
            "confidence": artifact.provenance.confidence,
        },
    }
