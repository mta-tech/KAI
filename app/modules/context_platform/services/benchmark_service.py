"""Benchmark service for execution and scoring.

Provides deterministic benchmark execution with severity-weighted scoring,
pass/fail evaluation, and export functionality.
"""

import uuid
from datetime import datetime
from typing import Any

from app.data.db.storage import Storage
from app.modules.context_platform.models.benchmark import (
    BenchmarkSuite,
    BenchmarkCase,
    BenchmarkRun,
    BenchmarkResult,
    CaseSeverity,
    CaseTag,
    ResultStatus,
    RunStatus,
)
from app.modules.context_platform.repositories.benchmark_repository import (
    BenchmarkRepository,
)


class BenchmarkService:
    """Service for benchmark execution and scoring.

    Features:
    - Deterministic pass/fail evaluation
    - Severity-weighted scoring
    - Failure fingerprint persistence
    - CI artifact export (JSON + JUnit XML)
    """

    def __init__(self, storage: Storage):
        self.storage = storage
        self.repository = BenchmarkRepository(storage)

    # ========================================================================
    # Suite Management
    # ========================================================================

    def create_suite(self, suite: BenchmarkSuite) -> str:
        """Create a new benchmark suite."""
        suite_id = self.repository.insert_suite(suite)
        return suite_id

    def get_suite(self, suite_id: str) -> dict | None:
        """Get a suite by ID."""
        return self.repository.find_suite_by_id(suite_id)

    def list_suites(
        self, db_connection_id: str | None = None, active_only: bool = True
    ) -> list[dict]:
        """List suites, optionally filtered by connection."""
        if db_connection_id:
            return self.repository.find_suites_by_connection(
                db_connection_id, active_only
            )
        # Get all active suites
        return self.storage.find_all(
            "benchmark_suites",
            filter_dict={"is_active": True} if active_only else None
        )

    def update_suite_metrics(
        self, suite_id: str, total_runs: int, avg_score: float
    ) -> bool:
        """Update suite metrics after a run."""
        return self.repository.update_suite(
            suite_id,
            {
                "total_runs": total_runs,
                "avg_score": avg_score,
                "last_run_at": datetime.now().isoformat(),
            }
        )

    # ========================================================================
    # Case Management
    # ========================================================================

    def create_case(self, case: BenchmarkCase) -> str:
        """Create a new benchmark case."""
        return self.repository.insert_case(case)

    def get_case(self, case_id: str) -> dict | None:
        """Get a case by ID."""
        return self.repository.find_case_by_id(case_id)

    def list_cases(self, suite_id: str) -> list[dict]:
        """List all cases in a suite."""
        return self.repository.find_cases_by_suite(suite_id)

    # ========================================================================
    # Benchmark Execution
    # ========================================================================

    def create_run(
        self, suite_id: str, db_connection_id: str, context_asset_ids: list[str] | None = None
    ) -> BenchmarkRun:
        """Create a new benchmark run."""
        run = BenchmarkRun(
            id=f"run_{uuid.uuid4().hex[:12]}",
            suite_id=suite_id,
            db_connection_id=db_connection_id,
            status=RunStatus.PENDING,
            context_asset_ids=context_asset_ids or [],
        )
        run_id = self.repository.insert_run(run)
        run.id = run_id
        return run

    def start_run(self, run_id: str) -> bool:
        """Mark a run as started."""
        return self.repository.update_run(
            run_id,
            {
                "status": RunStatus.RUNNING.value,
                "started_at": datetime.now().isoformat(),
            }
        )

    def execute_case(
        self,
        run_id: str,
        case_id: str,
        actual_sql: str | None = None,
        actual_result: dict | None = None,
        context_assets_used: list[str] | None = None,
        execution_time_ms: int = 0,
    ) -> BenchmarkResult:
        """Execute a single benchmark case and evaluate result.

        This is a deterministic evaluation - same inputs produce same outputs.
        The scoring is based on similarity to expected SQL and success criteria.
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Calculate similarity score
        similarity_score = self._calculate_similarity(
            case.get("expected_sql"),
            actual_sql,
            case.get("expected_result"),
            actual_result,
        )

        # Evaluate against success criteria
        success_criteria = case.get("success_criteria", {})
        passed = self._evaluate_success_criteria(
            similarity_score, success_criteria, execution_time_ms
        )

        # Calculate weighted score
        weight = case.get("weight", 1.0)
        severity = case.get("severity", CaseSeverity.MEDIUM.value)
        severity_multiplier = self._get_severity_multiplier(severity)
        weighted_score = weight * similarity_score * severity_multiplier

        # Determine status
        status = ResultStatus.PASSED if passed else ResultStatus.FAILED
        if execution_time_ms == 0 and not actual_sql:
            status = ResultStatus.SKIPPED

        # Create result
        result = BenchmarkResult(
            id=f"result_{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            case_id=case_id,
            status=status,
            actual_sql=actual_sql,
            actual_result=actual_result,
            similarity_score=similarity_score,
            execution_time_ms=execution_time_ms,
            weighted_score=weighted_score,
            passed=passed,
            context_assets_used=context_assets_used or [],
        )

        result_id = self.repository.insert_result(result)
        result.id = result_id
        return result

    def complete_run(self, run_id: str) -> dict:
        """Mark a run as completed and calculate aggregate metrics."""
        run = self.repository.find_run_by_id(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        results = self.repository.find_results_by_run(run_id)

        # Calculate aggregate metrics
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.get("status") == ResultStatus.PASSED.value)
        failed_cases = sum(1 for r in results if r.get("status") == ResultStatus.FAILED.value)
        skipped_cases = sum(1 for r in results if r.get("status") == ResultStatus.SKIPPED.value)
        error_cases = sum(1 for r in results if r.get("status") == ResultStatus.ERROR.value)

        # Calculate scores
        total_score = sum(r.get("weighted_score", 0.0) for r in results)
        max_score = sum(
            self._get_case_weight(c.get("case_id")) for c in results
        )
        weighted_score = (total_score / max_score * 100) if max_score > 0 else 0.0
        pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0.0

        # Severity breakdown
        severity_counts = self._calculate_severity_breakdown(run_id, results)

        updates = {
            "status": RunStatus.COMPLETED.value,
            "completed_at": datetime.now().isoformat(),
            "result_ids": [r.get("id") for r in results],
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "skipped_cases": skipped_cases,
            "error_cases": error_cases,
            "total_score": total_score,
            "max_score": max_score,
            "weighted_score": weighted_score,
            "pass_rate": pass_rate,
            **severity_counts,
        }

        self.repository.update_run(run_id, updates)

        # Update suite metrics
        self.update_suite_metrics(
            run.get("suite_id"),
            run.get("total_runs", 0) + 1,
            weighted_score
        )

        return self.repository.find_run_by_id(run_id)

    # ========================================================================
    # Scoring and Evaluation
    # ========================================================================

    def _calculate_similarity(
        self,
        expected_sql: str | None,
        actual_sql: str | None,
        expected_result: dict | None,
        actual_result: dict | None,
    ) -> float:
        """Calculate similarity between expected and actual.

        This is deterministic - same inputs always produce same output.
        Uses a combination of SQL similarity and result similarity.
        """
        if not expected_sql:
            # If no expected SQL, check result similarity
            if expected_result and actual_result:
                return self._result_similarity(expected_result, actual_result)
            return 1.0  # No expectation, so pass

        if not actual_sql:
            return 0.0

        # Simple SQL similarity (can be enhanced with more sophisticated algorithms)
        sql_sim = self._sql_similarity(expected_sql, actual_sql)

        # Result similarity if available
        result_sim = 1.0
        if expected_result and actual_result:
            result_sim = self._result_similarity(expected_result, actual_result)

        # Weighted combination
        return (sql_sim * 0.7 + result_sim * 0.3)

    def _sql_similarity(self, expected: str, actual: str) -> float:
        """Calculate SQL string similarity.

        Deterministic algorithm based on token overlap and structure.
        """
        # Normalize SQL
        expected_normalized = self._normalize_sql(expected)
        actual_normalized = self._normalize_sql(actual)

        if expected_normalized == actual_normalized:
            return 1.0

        # Token-based similarity
        expected_tokens = set(expected_normalized.split())
        actual_tokens = set(actual_normalized.split())

        if not expected_tokens:
            return 1.0
        if not actual_tokens:
            return 0.0

        intersection = expected_tokens & actual_tokens
        union = expected_tokens | actual_tokens

        return len(intersection) / len(union)

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison."""
        # Remove extra whitespace
        sql = " ".join(sql.split())
        # Convert to lowercase
        sql = sql.lower()
        # Remove trailing semicolon
        sql = sql.rstrip(";")
        return sql

    def _result_similarity(self, expected: dict, actual: dict) -> float:
        """Calculate result similarity."""
        # Simple key-value overlap
        if not expected or not actual:
            return 1.0

        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())

        if not expected_keys:
            return 1.0

        intersection = expected_keys & actual_keys
        if not intersection:
            return 0.0

        # Check values for matching keys
        matches = 0
        for key in intersection:
            if expected[key] == actual[key]:
                matches += 1

        return matches / len(intersection)

    def _evaluate_success_criteria(
        self, similarity_score: float, criteria: dict, execution_time_ms: int
    ) -> bool:
        """Evaluate if a result meets success criteria.

        Deterministic evaluation - same inputs always produce same output.
        """
        # Check minimum similarity
        min_similarity = criteria.get("min_similarity", 0.0)
        if similarity_score < min_similarity:
            return False

        # Check execution time
        max_time = criteria.get("max_execution_time_ms", None)
        if max_time and execution_time_ms > max_time:
            return False

        return True

    def _get_severity_multiplier(self, severity: str) -> float:
        """Get severity multiplier for scoring."""
        multipliers = {
            CaseSeverity.LOW.value: 0.5,
            CaseSeverity.MEDIUM.value: 1.0,
            CaseSeverity.HIGH.value: 1.5,
            CaseSeverity.CRITICAL.value: 2.0,
        }
        return multipliers.get(severity, 1.0)

    def _get_case_weight(self, case_id: str) -> float:
        """Get the effective weight of a case (weight * severity multiplier)."""
        case = self.repository.find_case_by_id(case_id)
        if not case:
            return 1.0

        weight = case.get("weight", 1.0)
        severity = case.get("severity", CaseSeverity.MEDIUM.value)
        severity_multiplier = self._get_severity_multiplier(severity)

        return weight * severity_multiplier

    def _calculate_severity_breakdown(
        self, run_id: str, results: list[dict]
    ) -> dict[str, int]:
        """Calculate pass/fail breakdown by severity."""
        breakdown = {
            "critical_passed": 0,
            "critical_total": 0,
            "high_passed": 0,
            "high_total": 0,
            "medium_passed": 0,
            "medium_total": 0,
            "low_passed": 0,
            "low_total": 0,
        }

        for result in results:
            case = self.repository.find_case_by_id(result.get("case_id", ""))
            if not case:
                continue

            severity = case.get("severity", CaseSeverity.MEDIUM.value)
            passed = result.get("status") == ResultStatus.PASSED.value

            if severity == CaseSeverity.CRITICAL.value:
                breakdown["critical_total"] += 1
                if passed:
                    breakdown["critical_passed"] += 1
            elif severity == CaseSeverity.HIGH.value:
                breakdown["high_total"] += 1
                if passed:
                    breakdown["high_passed"] += 1
            elif severity == CaseSeverity.MEDIUM.value:
                breakdown["medium_total"] += 1
                if passed:
                    breakdown["medium_passed"] += 1
            elif severity == CaseSeverity.LOW.value:
                breakdown["low_total"] += 1
                if passed:
                    breakdown["low_passed"] += 1

        return breakdown

    # ========================================================================
    # Export Operations
    # ========================================================================

    def export_run_json(self, run_id: str) -> dict | None:
        """Export run as JSON."""
        return self.repository.export_run_json(run_id)

    def export_run_junit(self, run_id: str) -> str | None:
        """Export run as JUnit XML for CI systems."""
        return self.repository.export_run_junit(run_id)

    def get_failure_fingerprint(self, result_id: str) -> dict | None:
        """Get a fingerprint of a failure for deduplication.

        Failure fingerprints help identify recurring issues across runs.
        """
        result = self.repository.find_result_by_id(result_id)
        if not result or result.get("status") != ResultStatus.FAILED.value:
            return None

        case = self.repository.find_case_by_id(result.get("case_id", ""))
        if not case:
            return None

        # Create fingerprint from stable characteristics
        fingerprint = {
            "case_id": result.get("case_id"),
            "severity": case.get("severity"),
            "error_type": self._classify_error(result.get("error_message", "")),
            "sql_hash": self._hash_sql(result.get("actual_sql", "")),
            "similarity_score": result.get("similarity_score"),
        }

        return fingerprint

    def _classify_error(self, error_message: str) -> str:
        """Classify error type for fingerprinting."""
        error_lower = error_message.lower()

        if "syntax" in error_lower or "parse" in error_lower:
            return "syntax_error"
        elif "table" in error_lower or "column" in error_lower:
            return "schema_error"
        elif "permission" in error_lower or "access" in error_lower:
            return "permission_error"
        elif "timeout" in error_lower or "time" in error_lower:
            return "timeout_error"
        else:
            return "unknown_error"

    def _hash_sql(self, sql: str) -> str:
        """Create a hash of SQL for deduplication."""
        if not sql:
            return ""
        import hashlib
        normalized = self._normalize_sql(sql)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
