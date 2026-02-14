"""Benchmark repository for Typesense storage.

Handles CRUD operations for benchmark suites, cases, runs, and results.
"""

import json
from typing import Any

from app.data.db.storage import Storage
from app.modules.context_platform.models.benchmark import (
    BenchmarkSuite,
    BenchmarkCase,
    BenchmarkRun,
    BenchmarkResult,
)


# Collection names
SUITE_COLLECTION = "benchmark_suites"
CASE_COLLECTION = "benchmark_cases"
RUN_COLLECTION = "benchmark_runs"
RESULT_COLLECTION = "benchmark_results"


class BenchmarkRepository:
    """Repository for benchmark data persistence.

    Provides CRUD operations for suites, cases, runs, and results.
    All operations are deterministic for reproducible benchmarking.
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    # ========================================================================
    # Suite Operations
    # ========================================================================

    def insert_suite(self, suite: BenchmarkSuite) -> str:
        """Insert a benchmark suite."""
        doc = suite.__dict__
        return self.storage.insert_one(SUITE_COLLECTION, doc)

    def find_suite_by_id(self, suite_id: str) -> dict | None:
        """Find a suite by ID."""
        return self.storage.find_by_id(SUITE_COLLECTION, suite_id)

    def find_suites_by_connection(
        self, db_connection_id: str, active_only: bool = True
    ) -> list[dict]:
        """Find all suites for a database connection."""
        filter_dict = {"db_connection_id": db_connection_id}
        if active_only:
            filter_dict["is_active"] = True
        return self.storage.find(SUITE_COLLECTION, filter_dict)

    def update_suite(self, suite_id: str, updates: dict) -> bool:
        """Update a suite."""
        existing = self.find_suite_by_id(suite_id)
        if not existing:
            return False
        # Remove fields that shouldn't be updated
        updates.pop("id", None)
        updates.pop("created_at", None)
        # Update updated_at
        from datetime import datetime
        updates["updated_at"] = datetime.now().isoformat()
        self.storage.update_or_create(
            SUITE_COLLECTION,
            {"id": suite_id},
            updates
        )
        return True

    def delete_suite(self, suite_id: str) -> bool:
        """Delete a suite."""
        try:
            self.storage.delete_by_id(SUITE_COLLECTION, suite_id)
            return True
        except Exception:
            return False

    # ========================================================================
    # Case Operations
    # ========================================================================

    def insert_case(self, case: BenchmarkCase) -> str:
        """Insert a benchmark case."""
        doc = self._serialize_case(case)
        return self.storage.insert_one(CASE_COLLECTION, doc)

    def find_case_by_id(self, case_id: str) -> dict | None:
        """Find a case by ID."""
        return self.storage.find_by_id(CASE_COLLECTION, case_id)

    def find_cases_by_suite(self, suite_id: str) -> list[dict]:
        """Find all cases in a suite."""
        results = self.storage.find(
            CASE_COLLECTION,
            {"suite_id": suite_id}
        )
        return results

    def find_cases_by_tag(self, tag: str) -> list[dict]:
        """Find cases with a specific tag."""
        # Note: Typesense doesn't support array contains natively
        # Using full text search on tags field
        results = self.storage.full_text_search(
            CASE_COLLECTION,
            tag,
            ["tags"]
        )
        return results

    def update_case(self, case_id: str, updates: dict) -> bool:
        """Update a case."""
        existing = self.find_case_by_id(case_id)
        if not existing:
            return False
        updates.pop("id", None)
        updates.pop("created_at", None)
        from datetime import datetime
        updates["updated_at"] = datetime.now().isoformat()
        self.storage.update_or_create(
            CASE_COLLECTION,
            {"id": case_id},
            updates
        )
        return True

    def delete_case(self, case_id: str) -> bool:
        """Delete a case."""
        try:
            self.storage.delete_by_id(CASE_COLLECTION, case_id)
            return True
        except Exception:
            return False

    # ========================================================================
    # Run Operations
    # ========================================================================

    def insert_run(self, run: BenchmarkRun) -> str:
        """Insert a benchmark run."""
        doc = self._serialize_run(run)
        return self.storage.insert_one(RUN_COLLECTION, doc)

    def find_run_by_id(self, run_id: str) -> dict | None:
        """Find a run by ID."""
        return self.storage.find_by_id(RUN_COLLECTION, run_id)

    def find_runs_by_suite(
        self, suite_id: str, limit: int = 50
    ) -> list[dict]:
        """Find runs for a suite, ordered by created_at desc."""
        results = self.storage.find(
            RUN_COLLECTION,
            {"suite_id": suite_id},
            sort=["created_at:desc"],
            limit=limit
        )
        return results

    def find_runs_by_status(self, status: str) -> list[dict]:
        """Find runs with a specific status."""
        results = self.storage.find(
            RUN_COLLECTION,
            {"status": status}
        )
        return results

    def update_run(self, run_id: str, updates: dict) -> bool:
        """Update a run."""
        existing = self.find_run_by_id(run_id)
        if not existing:
            return False
        updates.pop("id", None)
        updates.pop("created_at", None)
        self.storage.update_or_create(
            RUN_COLLECTION,
            {"id": run_id},
            updates
        )
        return True

    def delete_run(self, run_id: str) -> bool:
        """Delete a run."""
        try:
            self.storage.delete_by_id(RUN_COLLECTION, run_id)
            return True
        except Exception:
            return False

    # ========================================================================
    # Result Operations
    # ========================================================================

    def insert_result(self, result: BenchmarkResult) -> str:
        """Insert a benchmark result."""
        doc = self._serialize_result(result)
        return self.storage.insert_one(RESULT_COLLECTION, doc)

    def find_result_by_id(self, result_id: str) -> dict | None:
        """Find a result by ID."""
        return self.storage.find_by_id(RESULT_COLLECTION, result_id)

    def find_results_by_run(self, run_id: str) -> list[dict]:
        """Find all results for a run."""
        results = self.storage.find(
            RESULT_COLLECTION,
            {"run_id": run_id}
        )
        return results

    def find_results_by_case(self, case_id: str, limit: int = 100) -> list[dict]:
        """Find recent results for a case."""
        results = self.storage.find(
            RESULT_COLLECTION,
            {"case_id": case_id},
            sort=["created_at:desc"],
            limit=limit
        )
        return results

    def update_result(self, result_id: str, updates: dict) -> bool:
        """Update a result."""
        existing = self.find_result_by_id(result_id)
        if not existing:
            return False
        updates.pop("id", None)
        updates.pop("started_at", None)
        self.storage.update_or_create(
            RESULT_COLLECTION,
            {"id": result_id},
            updates
        )
        return True

    def delete_result(self, result_id: str) -> bool:
        """Delete a result."""
        try:
            self.storage.delete_by_id(RESULT_COLLECTION, result_id)
            return True
        except Exception:
            return False

    # ========================================================================
    # Serialization Helpers
    # ========================================================================

    def _serialize_case(self, case: BenchmarkCase) -> dict:
        """Serialize a BenchmarkCase to dict."""
        doc = case.__dict__.copy()
        # Convert enum values to strings
        if hasattr(case.tags, '__iter__'):
            doc["tags"] = [t.value if hasattr(t, 'value') else t for t in case.tags]
        if hasattr(case.severity, 'value'):
            doc["severity"] = case.severity.value
        return doc

    def _serialize_run(self, run: BenchmarkRun) -> dict:
        """Serialize a BenchmarkRun to dict."""
        doc = run.__dict__.copy()
        # Convert enum values to strings
        if hasattr(run.status, 'value'):
            doc["status"] = run.status.value
        return doc

    def _serialize_result(self, result: BenchmarkResult) -> dict:
        """Serialize a BenchmarkResult to dict."""
        doc = result.__dict__.copy()
        # Convert enum values to strings
        if hasattr(result.status, 'value'):
            doc["status"] = result.status.value
        return doc

    # ========================================================================
    # Export Operations
    # ========================================================================

    def export_run_json(self, run_id: str) -> dict | None:
        """Export a run and all its results as JSON."""
        run = self.find_run_by_id(run_id)
        if not run:
            return None

        results = self.find_results_by_run(run_id)

        return {
            "run": run,
            "results": results,
            "exported_at": self._get_timestamp()
        }

    def export_run_junit(self, run_id: str) -> str | None:
        """Export a run as JUnit XML for CI systems."""
        run = self.find_run_by_id(run_id)
        if not run:
            return None

        results = self.find_results_by_run(run_id)

        # Build JUnit XML
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuites name="{run.get("suite_id", "benchmark")}" '
            f'tests="{run.get("total_cases", 0)}" '
            f'failures="{run.get("failed_cases", 0)}" '
            f'errors="{run.get("error_cases", 0)}" '
            f'time="{run.get("execution_time_ms", 0) / 1000:.2f}">'
        ]

        xml_parts.append(f'  <testsuite name="{run.get("id", run_id)}" '
                       f'tests="{run.get("total_cases", 0)}" '
                       f'failures="{run.get("failed_cases", 0)}" '
                       f'errors="{run.get("error_cases", 0)}" '
                       f'time="{run.get("execution_time_ms", 0) / 1000:.2f}">')

        for result in results:
            case_id = result.get("case_id", "unknown")
            status = result.get("status", "skipped")
            execution_time = result.get("execution_time_ms", 0) / 1000.0

            xml_parts.append(f'    <testcase name="{case_id}" time="{execution_time:.2f}">')

            if status == "failed":
                error_msg = result.get("error_message", "Test failed")
                xml_parts.append(f'      <failure message="{self._escape_xml(error_msg)}"/>')
            elif status == "error":
                error_msg = result.get("error_message", "Test error")
                xml_parts.append(f'      <error message="{self._escape_xml(error_msg)}"/>')

            xml_parts.append('    </testcase>')

        xml_parts.append('  </testsuite>')
        xml_parts.append('</testsuites>')

        return "\n".join(xml_parts)

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _escape_xml(self, text: str) -> str:
        """Escape special characters for XML."""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;")
        )
