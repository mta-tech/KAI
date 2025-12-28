"""Analytics API endpoints."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.modules.analytics import (
    AnomalyService,
    ForecastingService,
    StatisticalService,
)
from app.modules.analytics.exceptions import (
    AnomalyDetectionError,
    CorrelationAnalysisError,
    ForecastingError,
    InvalidMethodError,
    StatisticalCalculationError,
)
from app.server.errors import error_response


router = APIRouter(prefix="/api/v2/analytics", tags=["Analytics"])


class DescriptiveStatsRequest(BaseModel):
    """Request for descriptive statistics."""

    data: list[float | int]
    column_name: str = "value"


class DescriptiveStatsResponse(BaseModel):
    """Response for descriptive statistics."""

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


class TTestRequest(BaseModel):
    """Request for t-test."""

    group1: list[float | int]
    group2: list[float | int]
    alpha: float = 0.05


class StatisticalTestResponse(BaseModel):
    """Response for statistical tests."""

    test_name: str
    test_type: str
    statistic: float
    p_value: float
    degrees_of_freedom: float | None = None
    is_significant: bool
    interpretation: str
    effect_size: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CorrelationRequest(BaseModel):
    """Request for correlation analysis."""

    x: list[float | int]
    y: list[float | int]
    method: str = "pearson"
    alpha: float = 0.05


class CorrelationResponse(BaseModel):
    """Response for correlation analysis."""

    method: str
    coefficient: float
    p_value: float
    is_significant: bool
    interpretation: str
    sample_size: int


class CorrelationMatrixRequest(BaseModel):
    """Request for correlation matrix."""

    data: list[dict[str, Any]]
    method: str = "pearson"


class CorrelationMatrixResponse(BaseModel):
    """Response for correlation matrix."""

    method: str
    matrix: dict[str, dict[str, float]]
    columns: list[str]


class AnomalyRequest(BaseModel):
    """Request for anomaly detection."""

    data: list[float | int]
    method: str = "zscore"
    threshold: float = 3.0


class AnomalyResponse(BaseModel):
    """Response for anomaly detection."""

    method: str
    total_points: int
    anomaly_count: int
    anomaly_percentage: float
    anomalies: list[dict[str, Any]]
    threshold: float | None = None
    interpretation: str


class ForecastRequest(BaseModel):
    """Request for forecasting."""

    values: list[float | int]
    periods: int = 30


class ForecastResponse(BaseModel):
    """Response for forecasting."""

    model_name: str
    forecast_dates: list[str]
    forecast_values: list[float]
    lower_bound: list[float]
    upper_bound: list[float]
    confidence_level: float
    trend: str
    interpretation: str


_stat_service = StatisticalService()
_anomaly_service = AnomalyService()
_forecast_service = ForecastingService()


@router.post("/descriptive", response_model=DescriptiveStatsResponse)
async def descriptive_statistics(
    request: DescriptiveStatsRequest,
) -> DescriptiveStatsResponse:
    """Calculate descriptive statistics for a dataset."""
    try:
        series = pd.Series(request.data, name=request.column_name)
        result = _stat_service.descriptive_stats(series)

        return DescriptiveStatsResponse(
            column=result.column,
            count=result.count,
            mean=result.mean,
            std=result.std,
            min=result.min,
            q25=result.q25,
            median=result.median,
            q75=result.q75,
            max=result.max,
            skewness=result.skewness,
            kurtosis=result.kurtosis,
        )
    except StatisticalCalculationError as e:
        return error_response(e, {"column_name": request.column_name})
    except Exception as e:
        wrapped_error = StatisticalCalculationError(
            f"Statistics calculation failed: {e}"
        )
        return error_response(wrapped_error, {"column_name": request.column_name})


@router.post("/t-test", response_model=StatisticalTestResponse)
async def t_test(request: TTestRequest) -> StatisticalTestResponse:
    """Perform independent samples t-test."""
    try:
        group1 = pd.Series(request.group1)
        group2 = pd.Series(request.group2)
        result = _stat_service.t_test_independent(group1, group2, alpha=request.alpha)

        return StatisticalTestResponse(
            test_name=result.test_name,
            test_type=result.test_type,
            statistic=result.statistic,
            p_value=result.p_value,
            degrees_of_freedom=result.degrees_of_freedom,
            is_significant=result.is_significant,
            interpretation=result.interpretation,
            effect_size=result.effect_size,
            details=result.details,
        )
    except StatisticalCalculationError as e:
        return error_response(e, {"alpha": request.alpha})
    except Exception as e:
        wrapped_error = StatisticalCalculationError(f"T-test failed: {e}")
        return error_response(wrapped_error, {"alpha": request.alpha})


@router.post("/correlation", response_model=CorrelationResponse)
async def correlation(request: CorrelationRequest) -> CorrelationResponse:
    """Calculate correlation between two variables."""
    try:
        x = pd.Series(request.x)
        y = pd.Series(request.y)
        result = _stat_service.correlation(
            x, y, method=request.method, alpha=request.alpha
        )

        return CorrelationResponse(
            method=result.method,
            coefficient=result.coefficient,
            p_value=result.p_value,
            is_significant=result.is_significant,
            interpretation=result.interpretation,
            sample_size=result.sample_size,
        )
    except CorrelationAnalysisError as e:
        return error_response(e, {"method": request.method, "alpha": request.alpha})
    except Exception as e:
        wrapped_error = CorrelationAnalysisError(f"Correlation analysis failed: {e}")
        return error_response(
            wrapped_error, {"method": request.method, "alpha": request.alpha}
        )


@router.post("/correlation-matrix", response_model=CorrelationMatrixResponse)
async def correlation_matrix(
    request: CorrelationMatrixRequest,
) -> CorrelationMatrixResponse:
    """Calculate correlation matrix for a dataset."""
    try:
        df = pd.DataFrame(request.data)
        result = _stat_service.correlation_matrix(df, method=request.method)

        return CorrelationMatrixResponse(
            method=result.method,
            matrix=result.matrix,
            columns=result.columns,
        )
    except CorrelationAnalysisError as e:
        return error_response(e, {"method": request.method})
    except Exception as e:
        wrapped_error = CorrelationAnalysisError(f"Correlation matrix failed: {e}")
        return error_response(wrapped_error, {"method": request.method})


@router.post("/anomalies", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest) -> AnomalyResponse:
    """Detect anomalies in a dataset."""
    try:
        series = pd.Series(request.data)

        if request.method == "zscore":
            result = _anomaly_service.detect_zscore(series, threshold=request.threshold)
        elif request.method == "iqr":
            result = _anomaly_service.detect_iqr(series, multiplier=request.threshold)
        else:
            raise InvalidMethodError(f"Unknown method: {request.method}")

        return AnomalyResponse(
            method=result.method,
            total_points=result.total_points,
            anomaly_count=result.anomaly_count,
            anomaly_percentage=result.anomaly_percentage,
            anomalies=result.anomalies,
            threshold=result.threshold,
            interpretation=result.interpretation,
        )
    except InvalidMethodError as e:
        return error_response(
            e, {"method": request.method, "threshold": request.threshold}
        )
    except AnomalyDetectionError as e:
        return error_response(
            e, {"method": request.method, "threshold": request.threshold}
        )
    except Exception as e:
        wrapped_error = AnomalyDetectionError(f"Anomaly detection failed: {e}")
        return error_response(
            wrapped_error, {"method": request.method, "threshold": request.threshold}
        )


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest) -> ForecastResponse:
    """Generate simple forecast for time series data."""
    try:
        series = pd.Series(request.values)
        result = _forecast_service.forecast_simple(series, periods=request.periods)

        return ForecastResponse(
            model_name=result.model_name,
            forecast_dates=result.forecast_dates,
            forecast_values=result.forecast_values,
            lower_bound=result.lower_bound,
            upper_bound=result.upper_bound,
            confidence_level=result.confidence_level,
            trend=result.trend,
            interpretation=result.interpretation,
        )
    except ForecastingError as e:
        return error_response(e, {"periods": request.periods})
    except Exception as e:
        wrapped_error = ForecastingError(f"Forecast failed: {e}")
        return error_response(wrapped_error, {"periods": request.periods})
