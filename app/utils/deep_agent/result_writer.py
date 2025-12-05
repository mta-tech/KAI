"""Result writer tool for Deep Agent SQL outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field

from app.server.errors import sql_agent_exceptions


class SqlResultWriterTool(BaseTool):
    """Persist SQL result rows to tenant-scoped storage."""

    name: str = "SqlResultWriter"
    description: str = """
    Input: JSON payload with `rows` (list of dict) and optional `columns`.
    Output: Location of the stored CSV. Use after executing SQL to capture large result sets.
    """

    result_dir: str
    tenant_id: str = Field(default="default")
    sql_generation_id: str = Field(default="session")

    @sql_agent_exceptions()
    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        payload = self._parse_payload(tool_input)
        rows: List[Dict[str, Any]] = payload.get("rows", [])
        columns = payload.get("columns")

        path = self._write_csv(rows, columns)
        return json.dumps({
            "message": f"Saved results to {path}",
            "files": [str(path)],
        })

    def _parse_payload(self, tool_input: str) -> Dict[str, Any]:
        if isinstance(tool_input, dict):
            return tool_input
        try:
            return json.loads(tool_input)
        except Exception:
            raise ValueError("SqlResultWriter expects JSON payload")

    def _write_csv(self, rows: List[Dict[str, Any]], columns: List[str] | None) -> Path:
        base = Path(self.result_dir) / self.tenant_id / self.sql_generation_id
        base.mkdir(parents=True, exist_ok=True)
        file_path = base / f"results_{uuid4().hex}.csv"

        if not rows and not columns:
            file_path.touch()
            return file_path

        import csv

        cols = columns or (list(rows[0].keys()) if rows else [])
        with open(file_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols)
            if cols:
                writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in cols})
        return file_path

