"""Context Platform models for KAI context asset lifecycle management.

The Context Platform provides reusable context assets (table descriptions,
glossaries, instructions, skills) that can be versioned, tagged, and shared
across missions and database connections.
"""

from app.modules.context_platform.models.asset import (
    ContextAsset,
    ContextAssetTag,
    ContextAssetVersion,
    LifecycleState,
)

from app.modules.context_platform.models.benchmark import (
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkRun,
    BenchmarkSuite,
    CaseSeverity,
    CaseTag,
    ResultStatus,
    RunStatus,
)

__all__ = [
    # Asset models
    "ContextAsset",
    "ContextAssetVersion",
    "ContextAssetTag",
    "LifecycleState",
    # Benchmark models
    "BenchmarkSuite",
    "BenchmarkCase",
    "BenchmarkRun",
    "BenchmarkResult",
    "CaseTag",
    "CaseSeverity",
    "RunStatus",
    "ResultStatus",
]
