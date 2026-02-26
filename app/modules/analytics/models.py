"""Analytics data models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats for analytics results."""

    JSON = "json"
    CSV = "csv"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request model for exporting analytics results."""

    format: ExportFormat = Field(
        default=ExportFormat.JSON,
        description="The format to export the data in (json, csv, or pdf)",
    )
    filename: str | None = Field(
        default=None,
        description="Optional custom filename for the export (without extension)",
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include metadata in the export",
    )


class ExportResponse(BaseModel):
    """Response model for export operations."""

    success: bool = Field(description="Whether the export was successful")
    format: ExportFormat = Field(description="The format of the exported data")
    filename: str = Field(description="The filename of the exported data")
    content_type: str = Field(description="The MIME type of the exported data")
    size_bytes: int | None = Field(
        default=None,
        description="Size of the exported data in bytes",
    )
    message: str | None = Field(
        default=None,
        description="Optional message about the export",
    )


class StatisticalTestType(str, Enum):
    """Types of statistical tests."""

    T_TEST_IND = "t_test_independent"
    T_TEST_PAIRED = "t_test_paired"
    T_TEST_ONE_SAMPLE = "t_test_one_sample"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    CORRELATION = "correlation"
    REGRESSION = "regression"


class StatisticalTestResult(BaseModel):
    """Result of a statistical test."""

    test_name: str
    test_type: str
    statistic: float
    p_value: float
    degrees_of_freedom: float | None = None
    confidence_level: float = 0.95
    is_significant: bool
    interpretation: str
    effect_size: float | None = None
    effect_size_name: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CorrelationResult(BaseModel):
    """Result of correlation analysis."""

    method: str
    coefficient: float
    p_value: float
    is_significant: bool
    interpretation: str
    sample_size: int


class CorrelationMatrixResult(BaseModel):
    """Result of correlation matrix analysis."""

    method: str
    matrix: dict[str, dict[str, float]]
    p_values: dict[str, dict[str, float]] | None = None
    columns: list[str]


class DescriptiveStats(BaseModel):
    """Descriptive statistics for a numeric column."""

    column: str
    count: int
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    skewness: float | None = None
    kurtosis: float | None = None


class ForecastResult(BaseModel):
    """Result of time series forecast."""

    model_name: str
    forecast_dates: list[str]
    forecast_values: list[float]
    lower_bound: list[float]
    upper_bound: list[float]
    confidence_level: float
    trend: str
    interpretation: str
    metrics: dict[str, Any] = Field(default_factory=dict)


class AnomalyResult(BaseModel):
    """Result of anomaly detection."""

    method: str
    total_points: int
    anomaly_count: int
    anomaly_percentage: float
    anomalies: list[dict[str, Any]]
    threshold: float | None = None
    interpretation: str
