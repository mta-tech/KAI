"""Analysis suggestions API endpoints."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.modules.analysis_suggestions.models import AnalysisSuggestionsResponse
from app.modules.analysis_suggestions.services import AnalysisSuggestionService
from app.modules.sql_generation.models import LLMConfig


class GenerateSuggestionsRequest(BaseModel):
    """Request for generating suggestions with custom configuration."""

    llm_config: LLMConfig | None = None
    max_suggestions: int = 8


def create_suggestions_router(service: AnalysisSuggestionService) -> APIRouter:
    """Create FastAPI router for analysis suggestions."""

    router = APIRouter(prefix="/api/v1/suggestions", tags=["Analysis Suggestions"])

    @router.get("/{db_connection_id}", response_model=AnalysisSuggestionsResponse)
    async def get_suggestions(
        db_connection_id: str,
        max_suggestions: int = Query(default=8, ge=1, le=20),
    ):
        """
        Get analysis suggestions for a database connection.

        Generates suggestions based on MDL manifest and sample data using LLM.
        Falls back to rule-based suggestions if LLM fails.
        """
        try:
            return await service.generate_suggestions(
                db_connection_id=db_connection_id,
                max_suggestions=max_suggestions,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{db_connection_id}", response_model=AnalysisSuggestionsResponse)
    async def generate_suggestions(
        db_connection_id: str,
        request: GenerateSuggestionsRequest,
    ):
        """
        Generate analysis suggestions with custom LLM configuration.

        Allows specifying a different LLM model or configuration.
        """
        try:
            return await service.generate_suggestions(
                db_connection_id=db_connection_id,
                max_suggestions=request.max_suggestions,
                llm_config=request.llm_config,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router


__all__ = ["create_suggestions_router", "GenerateSuggestionsRequest"]
