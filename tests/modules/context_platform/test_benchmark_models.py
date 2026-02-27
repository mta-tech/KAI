# tests/modules/context_platform/test_benchmark_models.py
"""Tests for Benchmark models."""
import pytest
from app.modules.context_platform.models.benchmark import (
    BenchmarkCase,
    BenchmarkSuite,
    BenchmarkRun,
    BenchmarkResult,
    CaseTag,
    CaseSeverity,
    RunStatus,
    ResultStatus,
)


class TestBenchmarkCase:
    """Tests for BenchmarkCase model."""

    def test_create_benchmark_case(self):
        """Should create benchmark case with required fields."""
        case = BenchmarkCase(
            id="case_1",
            suite_id="suite_1",
            name="Sales by Region",
            question="Show sales by region",
        )
        assert case.id == "case_1"
        assert case.suite_id == "suite_1"
        assert case.question == "Show sales by region"


class TestBenchmarkSuite:
    """Tests for BenchmarkSuite model."""

    def test_create_benchmark_suite(self):
        """Should create benchmark suite."""
        suite = BenchmarkSuite(
            id="suite_1",
            name="Sales Benchmark",
            db_connection_id="db_456",
        )
        assert suite.id == "suite_1"
        assert suite.db_connection_id == "db_456"
        assert suite.is_active is True


class TestBenchmarkRun:
    """Tests for BenchmarkRun model."""

    def test_create_benchmark_run(self):
        """Should create benchmark run."""
        run = BenchmarkRun(
            id="run_1",
            suite_id="suite_1",
            db_connection_id="db_456",
        )
        assert run.id == "run_1"
        assert run.status == RunStatus.PENDING


class TestBenchmarkResult:
    """Tests for BenchmarkResult model."""

    def test_create_benchmark_result(self):
        """Should create benchmark result."""
        result = BenchmarkResult(
            id="result_1",
            run_id="run_1",
            case_id="case_1",
            status=ResultStatus.PASSED,
        )
        assert result.id == "result_1"
        assert result.status == ResultStatus.PASSED
