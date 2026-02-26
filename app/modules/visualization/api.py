"""Visualization API endpoints."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from app.modules.visualization import (
    ChartConfig,
    ChartService,
    ChartType,
    ThemeService,
)
from app.modules.visualization.exceptions import (
    ChartGenerationError,
    ChartRecommendationError,
    InvalidChartTypeError,
)
from app.server.errors import error_response


router = APIRouter(prefix="/api/v2/visualizations", tags=["Visualizations"])


class GenerateChartRequest(BaseModel):
    """Request model for chart generation."""

    data: list[dict[str, Any]]
    chart_type: str
    x_column: str | None = None
    y_column: str | None = None
    color_column: str | None = None
    size_column: str | None = None
    title: str | None = None
    theme: str = "default"
    width: int = 800
    height: int = 600
    interactive: bool = True


class ChartResponse(BaseModel):
    """Response model for chart generation."""

    chart_type: str
    html: str | None = None
    image_base64: str | None = None
    title: str | None = None


class RecommendChartRequest(BaseModel):
    """Request for chart recommendation."""

    data: list[dict[str, Any]]
    x_column: str | None = None
    y_column: str | None = None


class RecommendChartResponse(BaseModel):
    """Response for chart recommendation."""

    chart_type: str
    confidence: float
    rationale: str
    x_column: str | None = None
    y_column: str | None = None


class ThemeListResponse(BaseModel):
    """Response for theme listing."""

    themes: list[str]


_chart_service = ChartService()
_theme_service = ThemeService()


@router.post("/generate", response_model=ChartResponse)
async def generate_chart(request: GenerateChartRequest) -> ChartResponse:
    """Generate a chart from provided data."""
    try:
        df = pd.DataFrame(request.data)
        chart_type = ChartType(request.chart_type)

        config = ChartConfig(
            chart_type=chart_type,
            x_column=request.x_column,
            y_column=request.y_column,
            color_column=request.color_column,
            size_column=request.size_column,
            title=request.title,
            theme=request.theme,
            width=request.width,
            height=request.height,
            interactive=request.interactive,
        )

        result = _chart_service.generate_chart(df, config)

        image_base64 = None
        if not request.interactive:
            image_base64 = _chart_service.export_to_base64(result)

        return ChartResponse(
            chart_type=result.chart_type,
            html=result.html,
            image_base64=image_base64,
            title=request.title,
        )

    except InvalidChartTypeError as e:
        return error_response(
            e, {"chart_type": request.chart_type, "theme": request.theme}
        )
    except ChartGenerationError as e:
        return error_response(
            e, {"chart_type": request.chart_type, "theme": request.theme}
        )
    except ValueError as e:
        wrapped_error = InvalidChartTypeError(str(e))
        return error_response(
            wrapped_error, {"chart_type": request.chart_type, "theme": request.theme}
        )
    except Exception as e:
        wrapped_error = ChartGenerationError(f"Chart generation failed: {e}")
        return error_response(
            wrapped_error, {"chart_type": request.chart_type, "theme": request.theme}
        )


@router.post("/recommend", response_model=RecommendChartResponse)
async def recommend_chart(request: RecommendChartRequest) -> RecommendChartResponse:
    """Recommend optimal chart type for data."""
    try:
        df = pd.DataFrame(request.data)
        rec = _chart_service.recommend_chart_type(
            df,
            x_column=request.x_column,
            y_column=request.y_column,
        )

        return RecommendChartResponse(
            chart_type=rec.chart_type.value,
            confidence=rec.confidence,
            rationale=rec.rationale,
            x_column=rec.x_column,
            y_column=rec.y_column,
        )

    except ChartRecommendationError as e:
        return error_response(
            e, {"x_column": request.x_column, "y_column": request.y_column}
        )
    except Exception as e:
        wrapped_error = ChartRecommendationError(f"Recommendation failed: {e}")
        return error_response(
            wrapped_error, {"x_column": request.x_column, "y_column": request.y_column}
        )


@router.get("/themes", response_model=ThemeListResponse)
async def list_themes() -> ThemeListResponse:
    """List available chart themes."""
    return ThemeListResponse(themes=_theme_service.list_themes())


@router.get("/types")
async def list_chart_types() -> dict[str, list[str]]:
    """List available chart types."""
    return {"chart_types": [t.value for t in ChartType]}
