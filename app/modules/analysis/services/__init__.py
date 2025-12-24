"""Analysis service for comprehensive SQL result analysis."""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from app.api.requests import PromptRequest
from app.modules.analysis.models import AnalysisResult
from app.modules.analysis.repositories import AnalysisRepository
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.prompt.models import Prompt
from app.modules.prompt.repositories import PromptRepository
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.sql_generation.services import SQLGenerationService
from app.utils.analysis_generator import AnalysisAgent
from app.utils.sql_database.sql_database import SQLDatabase

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for generating comprehensive analysis from SQL results."""

    def __init__(self, storage):
        self.storage = storage
        self.repository = AnalysisRepository(storage)
        self.sql_generation_repository = SQLGenerationRepository(storage)
        self.prompt_repository = PromptRepository(storage)
        self.db_connection_repository = DatabaseConnectionRepository(storage)

    async def create_analysis(
        self,
        sql_generation_id: str,
        llm_config: LLMConfig | None = None,
        max_rows: int = 100,
        metadata: dict | None = None,
    ) -> AnalysisResult:
        """Create comprehensive analysis for an existing SQL generation.

        Args:
            sql_generation_id: ID of the SQL generation to analyze
            llm_config: LLM configuration for analysis
            max_rows: Maximum rows to fetch for analysis
            metadata: Additional metadata

        Returns:
            AnalysisResult with summary, insights, and chart recommendations
        """
        # Fetch SQL generation
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise HTTPException(
                status_code=404,
                detail=f"SQL Generation {sql_generation_id} not found",
            )

        if sql_generation.status == "INVALID":
            raise HTTPException(
                status_code=400,
                detail="Cannot analyze invalid SQL generation",
            )

        # Fetch prompt and database connection
        prompt = self.prompt_repository.find_by_id(sql_generation.prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt {sql_generation.prompt_id} not found",
            )

        db_connection = self.db_connection_repository.find_by_id(prompt.db_connection_id)
        if not db_connection:
            raise HTTPException(
                status_code=404,
                detail=f"Database connection {prompt.db_connection_id} not found",
            )

        # Execute SQL query
        database = SQLDatabase.get_sql_engine(db_connection, False)
        query_results = await self._execute_query_async(
            database, sql_generation.sql, max_rows
        )

        # Generate analysis
        agent = AnalysisAgent(llm_config=llm_config or LLMConfig())
        analysis = await agent.execute(
            sql_generation=sql_generation,
            query_results=query_results,
            user_prompt=prompt.text,
            database_connection=db_connection,
        )

        # Add metadata
        if metadata:
            analysis.metadata = {**(analysis.metadata or {}), **metadata}

        # Persist and return
        return self.repository.insert(analysis)

    async def create_comprehensive_analysis(
        self,
        prompt_request: PromptRequest,
        llm_config: LLMConfig | None = None,
        max_rows: int = 100,
        use_deep_agent: bool = False,
        metadata: dict | None = None,
    ) -> dict:
        """End-to-end pipeline: Prompt -> SQL Gen -> Execution -> Analysis.

        Args:
            prompt_request: The prompt request with text and db_connection_id
            llm_config: LLM configuration for SQL generation and analysis
            max_rows: Maximum rows to fetch for analysis
            use_deep_agent: Whether to use the deep agent for SQL generation
            metadata: Additional metadata

        Returns:
            Dict with prompt_id, sql_generation_id, sql, status, and analysis
        """
        start_time = datetime.now()
        timing = {}

        # Step 1: Create prompt
        prompt_start = datetime.now()
        prompt_service = PromptService(self.storage)
        prompt = prompt_service.create_prompt(prompt_request)
        timing["prompt_creation"] = (datetime.now() - prompt_start).total_seconds()

        # Step 2: Generate SQL
        sql_start = datetime.now()
        sql_generation_service = SQLGenerationService(self.storage)

        from app.api.requests import SQLGenerationRequest

        sql_request = SQLGenerationRequest(
            llm_config=llm_config or LLMConfig(),
            metadata={
                "use_deep_agent": use_deep_agent,
                **(metadata or {}),
            },
        )

        # Run SQL generation in thread pool (it's sync)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            sql_generation = await loop.run_in_executor(
                executor,
                sql_generation_service.create_sql_generation,
                prompt.id,
                sql_request,
            )
        timing["sql_generation"] = (datetime.now() - sql_start).total_seconds()

        # Step 3: Execute SQL and analyze
        analysis_start = datetime.now()

        if sql_generation.status == "VALID":
            # Fetch database connection
            db_connection = self.db_connection_repository.find_by_id(
                prompt.db_connection_id
            )
            database = SQLDatabase.get_sql_engine(db_connection, False)

            # Execute query
            query_results = await self._execute_query_async(
                database, sql_generation.sql, max_rows
            )

            # Generate analysis
            agent = AnalysisAgent(llm_config=llm_config or LLMConfig())
            analysis = await agent.execute(
                sql_generation=sql_generation,
                query_results=query_results,
                user_prompt=prompt.text,
                database_connection=db_connection,
            )

            # Persist analysis
            analysis = self.repository.insert(analysis)
        else:
            # Create error analysis
            analysis = AnalysisResult(
                sql_generation_id=sql_generation.id,
                prompt_id=prompt.id,
                llm_config=llm_config,
                summary=f"SQL generation failed: {sql_generation.error or 'Invalid SQL'}",
                error=sql_generation.error,
                completed_at=datetime.now().isoformat(),
            )
            analysis = self.repository.insert(analysis)

        timing["analysis"] = (datetime.now() - analysis_start).total_seconds()
        timing["total"] = (datetime.now() - start_time).total_seconds()

        return {
            "prompt_id": prompt.id,
            "sql_generation_id": sql_generation.id,
            "sql": sql_generation.sql,
            "sql_status": sql_generation.status,
            "analysis_id": analysis.id,
            "summary": analysis.summary,
            "insights": [
                insight.model_dump() if hasattr(insight, "model_dump") else insight
                for insight in analysis.insights
            ],
            "chart_recommendations": [
                rec.model_dump() if hasattr(rec, "model_dump") else rec
                for rec in analysis.chart_recommendations
            ],
            "row_count": analysis.row_count,
            "column_count": analysis.column_count,
            "input_tokens_used": (
                (sql_generation.input_tokens_used or 0) +
                (analysis.input_tokens_used or 0)
            ),
            "output_tokens_used": (
                (sql_generation.output_tokens_used or 0) +
                (analysis.output_tokens_used or 0)
            ),
            "error": analysis.error,
            "execution_time": timing,
        }

    async def _execute_query_async(
        self,
        database: SQLDatabase,
        sql: str,
        max_rows: int,
    ) -> list[dict]:
        """Execute SQL query asynchronously."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: database.run_sql(sql, max_rows),
            )
        # run_sql returns (str, dict) - we want the dict's 'result' key
        if isinstance(result, tuple) and len(result) > 1:
            result_dict = result[1]
            return result_dict.get("result", [])
        return []

    def get_analysis(self, analysis_id: str) -> AnalysisResult:
        """Get an analysis result by ID."""
        analysis = self.repository.find_by_id(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found",
            )
        return analysis

    def get_analyses_for_sql_generation(
        self, sql_generation_id: str
    ) -> list[AnalysisResult]:
        """Get all analyses for a SQL generation."""
        return self.repository.find_by_sql_generation_id(sql_generation_id)

