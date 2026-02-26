"""Chart visualization API endpoints for JavaScript chart libraries."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.modules.chartviz.exceptions import (
    AnalysisDataExtractionError,
    AutoChartGenerationError,
    ChartVizGenerationError,
    ChartVizRecommendationError,
    InvalidChartTypeError,
)
from app.modules.chartviz.models import (
    ChartType,
    ChartWidget,
    ChartRecommendation,
    GenerateChartRequest,
    RecommendChartRequest,
    AutoChartRequest,
)
from app.modules.chartviz.service import ChartVizService
from app.server.errors import error_response


router = APIRouter(prefix="/api/v2/chartviz", tags=["Chart Visualization"])

# Service instance (will be configured on first use)
_service: ChartVizService | None = None


def get_service() -> ChartVizService:
    """Get or create the chart visualization service."""
    global _service
    if _service is None:
        _service = ChartVizService()
    return _service


@router.post("/generate", response_model=ChartWidget)
async def generate_chart(request: GenerateChartRequest) -> ChartWidget:
    """Generate chart configuration for a specific chart type.

    This endpoint generates a chart widget configuration that can be
    directly used by JavaScript chart libraries like Chart.js, ECharts,
    Recharts, D3.js, or Plotly.js.

    Args:
        request: Chart generation request with data, type, and options

    Returns:
        ChartWidget configuration ready for JS rendering
    """
    try:
        service = get_service()
        return await service.generate_chart(
            data=request.data,
            chart_type=request.chart_type,
            user_prompt=request.user_prompt,
            language=request.language,
        )
    except ChartVizGenerationError as e:
        return error_response(
            e, {"chart_type": request.chart_type.value if request.chart_type else None}
        )
    except InvalidChartTypeError as e:
        return error_response(
            e, {"chart_type": request.chart_type.value if request.chart_type else None}
        )
    except ValueError as e:
        wrapped_error = InvalidChartTypeError(str(e))
        return error_response(
            wrapped_error,
            {"chart_type": request.chart_type.value if request.chart_type else None},
        )
    except Exception as e:
        wrapped_error = ChartVizGenerationError(f"Chart generation failed: {e}")
        return error_response(
            wrapped_error,
            {"chart_type": request.chart_type.value if request.chart_type else None},
        )


@router.post("/recommend", response_model=ChartRecommendation)
async def recommend_chart(request: RecommendChartRequest) -> ChartRecommendation:
    """Recommend the best chart type for the provided data.

    Uses AI to analyze the data structure and user context to
    recommend the most suitable chart type with confidence score.

    Args:
        request: Data and context for recommendation

    Returns:
        ChartRecommendation with type, confidence, and rationale
    """
    try:
        service = get_service()
        return await service.recommend_chart(
            data=request.data,
            user_prompt=request.user_prompt,
            language=request.language,
        )
    except ChartVizRecommendationError as e:
        return error_response(e, {"user_prompt": request.user_prompt})
    except ValueError as e:
        wrapped_error = ChartVizRecommendationError(str(e))
        return error_response(wrapped_error, {"user_prompt": request.user_prompt})
    except Exception as e:
        wrapped_error = ChartVizRecommendationError(f"Chart recommendation failed: {e}")
        return error_response(wrapped_error, {"user_prompt": request.user_prompt})


@router.post("/auto", response_model=ChartWidget)
async def auto_generate_chart(request: AutoChartRequest) -> ChartWidget:
    """Automatically recommend and generate chart in one call.

    Combines recommendation and generation: first recommends the best
    chart type, then generates the configuration.

    Args:
        request: Data and context for auto-generation

    Returns:
        ChartWidget with AI-selected chart type
    """
    try:
        service = get_service()
        return await service.auto_generate(
            data=request.data,
            user_prompt=request.user_prompt,
            language=request.language,
        )
    except AutoChartGenerationError as e:
        return error_response(e, {"user_prompt": request.user_prompt})
    except ValueError as e:
        wrapped_error = AutoChartGenerationError(str(e))
        return error_response(wrapped_error, {"user_prompt": request.user_prompt})
    except Exception as e:
        wrapped_error = AutoChartGenerationError(f"Auto chart generation failed: {e}")
        return error_response(wrapped_error, {"user_prompt": request.user_prompt})


@router.get("/types")
async def list_chart_types() -> dict[str, list[dict[str, str]]]:
    """List all available chart types with descriptions.

    Returns:
        Dict with list of chart type info
    """
    from app.modules.chartviz.prompts import get_chart_type_descriptions

    descriptions = get_chart_type_descriptions("en")
    return {
        "chart_types": [
            {
                "type": chart_type.value,
                "description": desc,
            }
            for chart_type, desc in descriptions.items()
        ]
    }


@router.post("/from-analysis", response_model=ChartWidget)
async def generate_from_analysis(
    analysis_result: dict[str, Any],
    chart_type: ChartType | None = None,
    language: str = "id",
) -> ChartWidget:
    """Generate chart from an analysis service result.

    Extracts data from the analysis result and generates a chart.
    If chart_type is not specified, auto-recommends the best type.

    Args:
        analysis_result: Result from AnalysisService
        chart_type: Optional specific chart type
        language: Language for labels

    Returns:
        ChartWidget configuration
    """
    try:
        service = get_service()
        return await service.generate_from_analysis(
            analysis_result=analysis_result,
            chart_type=chart_type,
            language=language,
        )
    except AnalysisDataExtractionError as e:
        return error_response(
            e, {"chart_type": chart_type.value if chart_type else None}
        )
    except ChartVizGenerationError as e:
        return error_response(
            e, {"chart_type": chart_type.value if chart_type else None}
        )
    except ValueError as e:
        wrapped_error = AnalysisDataExtractionError(str(e))
        return error_response(
            wrapped_error, {"chart_type": chart_type.value if chart_type else None}
        )
    except Exception as e:
        wrapped_error = AnalysisDataExtractionError(
            f"Chart generation from analysis failed: {e}"
        )
        return error_response(
            wrapped_error, {"chart_type": chart_type.value if chart_type else None}
        )


__all__ = ["router"]
