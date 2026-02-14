"""Benchmark system models for evaluating context asset quality.

Benchmarks are test cases used to evaluate the quality and effectiveness of
context assets (verified SQL, instructions, skills, etc.) in improving
autonomous agent performance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CaseTag(str, Enum):
    """Tags for categorizing benchmark cases."""

    SMOKE = "smoke"  # Basic functionality tests
    CRITICAL = "critical"  # Critical path tests
    DOMAIN = "domain"  # Domain-specific tests
    REGRESSION = "regression"  # Catch regressions
    PERFORMANCE = "performance"  # Performance-related tests


class CaseSeverity(str, Enum):
    """Severity level for benchmark cases."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RunStatus(str, Enum):
    """Status of a benchmark run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResultStatus(str, Enum):
    """Status of an individual benchmark result."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class BenchmarkCase:
    """A single benchmark test case.

    Cases are reusable test scenarios that can be run against different
    context assets to measure their effectiveness.
    """

    id: str
    suite_id: str
    name: str
    question: str  # Natural language question to test
    description: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Test configuration
    expected_sql: str | None = None  # Expected SQL query (for SQL benchmarks)
    expected_result: dict[str, Any] | None = None  # Expected result structure/values

    # Categorization
    tags: list[CaseTag] = field(default_factory=list)
    severity: CaseSeverity = CaseSeverity.MEDIUM
    domain: str | None = None  # Domain area (e.g., 'sales', 'inventory', 'finance')

    # Context requirements
    required_asset_types: list[str] = field(default_factory=list)  # Asset types needed for this case
    required_tables: list[str] = field(default_factory=list)  # Database tables required

    # Evaluation criteria
    success_criteria: dict[str, Any] = field(default_factory=dict)  # Criteria for passing
    weight: float = 1.0  # Weight for scoring (higher = more important)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    author: str | None = None
    version: str = "1.0.0"


@dataclass
class BenchmarkSuite:
    """A collection of benchmark cases.

    Suites group related test cases for running together.
    """

    id: str
    name: str
    db_connection_id: str  # Database connection to run benchmarks against
    description: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Suite configuration
    context_asset_filter: dict[str, Any] = field(default_factory=dict)  # Filter for context assets

    # Test cases
    case_ids: list[str] = field(default_factory=list)  # IDs of BenchmarkCases in this suite

    # Suite metadata
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    is_active: bool = True

    # Metrics
    total_runs: int = 0
    avg_score: float = 0.0
    last_run_at: str | None = None


@dataclass
class BenchmarkResult:
    """Result from running a single benchmark case."""

    id: str
    run_id: str
    case_id: str
    status: ResultStatus

    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str | None = None

    # Actual results
    actual_sql: str | None = None
    actual_result: dict[str, Any] | None = None

    # Evaluation
    similarity_score: float | None = None  # Similarity to expected SQL (0-1)
    execution_time_ms: int = 0
    error_message: str | None = None

    # Weighted scoring
    weighted_score: float = 0.0  # Score weighted by case severity and weight
    passed: bool = False

    # Context used
    context_assets_used: list[str] = field(default_factory=list)  # IDs of context assets used

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkRun:
    """Execution of a benchmark suite.

    Tracks the overall execution and aggregated results.
    """

    id: str
    suite_id: str
    db_connection_id: str
    status: RunStatus = RunStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: str | None = None
    completed_at: str | None = None

    # Execution configuration
    context_asset_ids: list[str] = field(default_factory=list)

    # Results
    result_ids: list[str] = field(default_factory=list)

    # Aggregated metrics
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    skipped_cases: int = 0
    error_cases: int = 0

    # Score calculation
    total_score: float = 0.0  # Unweighted sum of all case scores
    max_score: float = 0.0  # Maximum possible score (sum of all weights)
    weighted_score: float = 0.0  # Final weighted score (0-100)
    pass_rate: float = 0.0  # Percentage of cases passed (0-100)

    # Severity breakdown
    critical_passed: int = 0
    critical_total: int = 0
    high_passed: int = 0
    high_total: int = 0
    medium_passed: int = 0
    medium_total: int = 0
    low_passed: int = 0
    low_total: int = 0

    # Execution metadata
    execution_time_ms: int = 0
    error: str | None = None

    # Comparison
    baseline_run_id: str | None = None  # Compare results against this baseline run
    score_delta: float | None = None  # Change in score from baseline

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    triggered_by: str | None = None  # What triggered this run (e.g., 'manual', 'ci', 'asset_update')
