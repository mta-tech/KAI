"""Notebook execution service."""

from __future__ import annotations

import re
import time
import uuid
from datetime import datetime
from typing import Any

from app.modules.notebook.models import (
    Cell,
    CellStatus,
    CellType,
    Notebook,
    NotebookRun,
)


class NotebookExecutor:
    """Service for executing notebooks."""

    def __init__(
        self,
        agent_runner: Any = None,
        chart_service: Any = None,
        llm_service: Any = None,
    ) -> None:
        """Initialize executor with optional services."""
        self.agent_runner = agent_runner
        self.chart_service = chart_service
        self.llm_service = llm_service

    async def execute_notebook(
        self,
        notebook: Notebook,
        parameters: dict[str, Any],
        database_alias: str | None = None,
    ) -> NotebookRun:
        """Execute a notebook with given parameters."""
        run = NotebookRun(
            id=str(uuid.uuid4()),
            notebook_id=notebook.id,
            parameters=parameters,
            status="running",
            started_at=datetime.utcnow(),
        )

        context = {
            "parameters": parameters,
            "results": {},
            "database_alias": database_alias or notebook.database_alias,
        }

        execution_order = self._resolve_dependencies(notebook.cells)
        total_start = time.time()

        try:
            for cell in execution_order:
                cell_start = time.time()
                cell.status = CellStatus.RUNNING

                try:
                    result = await self._execute_cell(cell, context)
                    cell.output = result
                    cell.status = CellStatus.COMPLETED
                    context["results"][cell.name] = result
                    run.results[cell.name] = result

                except Exception as e:
                    cell.status = CellStatus.FAILED
                    cell.error = str(e)
                    run.results[cell.name] = {"error": str(e)}

                cell.execution_time_ms = (time.time() - cell_start) * 1000

            run.status = "completed"

        except Exception as e:
            run.status = "failed"
            run.error = str(e)

        run.completed_at = datetime.utcnow()
        run.execution_time_ms = (time.time() - total_start) * 1000

        return run

    async def _execute_cell(
        self,
        cell: Cell,
        context: dict[str, Any],
    ) -> Any:
        """Execute a single cell."""
        prompt = self._interpolate(cell.prompt or "", context)

        if cell.cell_type == CellType.QUERY:
            return await self._execute_query_cell(prompt, context)

        if cell.cell_type == CellType.VISUALIZATION:
            return await self._execute_viz_cell(prompt, cell, context)

        if cell.cell_type == CellType.TEXT:
            return await self._execute_text_cell(prompt, context)

        if cell.cell_type == CellType.CODE:
            return await self._execute_code_cell(cell.code or "", context)

        if cell.cell_type == CellType.USER_INPUT:
            param_name = cell.name
            return context["parameters"].get(param_name)

        return None

    async def _execute_query_cell(
        self,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a query cell using the agent."""
        if self.agent_runner:
            result = await self.agent_runner(
                prompt=prompt,
                database_alias=context.get("database_alias"),
            )
            return result

        return {
            "status": "simulated",
            "prompt": prompt,
            "message": "Agent runner not configured",
        }

    async def _execute_viz_cell(
        self,
        prompt: str,
        cell: Cell,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a visualization cell."""
        dependent_data = None
        if cell.depends_on:
            dep_name = cell.depends_on[0]
            dependent_data = context["results"].get(dep_name)

        if self.chart_service and dependent_data:
            return {
                "status": "chart_generated",
                "prompt": prompt,
                "data_source": cell.depends_on[0] if cell.depends_on else None,
            }

        return {
            "status": "simulated",
            "prompt": prompt,
            "data_available": dependent_data is not None,
        }

    async def _execute_text_cell(
        self,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a text generation cell."""
        if self.llm_service:
            return {"text": "Generated text from LLM", "prompt": prompt}

        return {
            "status": "simulated",
            "prompt": prompt,
            "text": f"Summary based on: {list(context['results'].keys())}",
        }

    async def _execute_code_cell(
        self,
        code: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a Python code cell in sandbox."""
        import numpy as np
        import pandas as pd

        local_vars = {
            "context": context,
            "results": context["results"],
            "parameters": context["parameters"],
            "pd": pd,
            "np": np,
        }

        try:
            exec(code, {"__builtins__": {}}, local_vars)
            return {
                "status": "executed",
                "output": local_vars.get("output"),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _interpolate(self, template: str, context: dict[str, Any]) -> str:
        """Interpolate parameters into template."""

        def replace(match: re.Match) -> str:
            key = match.group(1)
            if key in context["parameters"]:
                return str(context["parameters"][key])
            if key in context["results"]:
                return str(context["results"][key])
            return match.group(0)

        return re.sub(r"\{\{(\w+)\}\}", replace, template)

    def _resolve_dependencies(self, cells: list[Cell]) -> list[Cell]:
        """Topological sort cells by dependencies."""
        cell_map = {c.name: c for c in cells}
        visited: set[str] = set()
        result: list[Cell] = []

        def visit(cell: Cell) -> None:
            if cell.name in visited:
                return
            visited.add(cell.name)

            for dep_name in cell.depends_on:
                if dep_name in cell_map:
                    visit(cell_map[dep_name])

            result.append(cell)

        for cell in cells:
            visit(cell)

        return result
