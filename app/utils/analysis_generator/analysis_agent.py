"""Analysis agent for generating comprehensive insights from SQL results."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback

from app.modules.analysis.models import (
    AnalysisResult,
    ChartRecommendation,
    Insight,
)
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.utils.analysis_generator.prompts import (
    ANALYSIS_USER_TEMPLATE,
    get_analysis_system_prompt,
)
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent for generating comprehensive analysis from SQL query results."""

    def __init__(self, llm_config: LLMConfig | None = None):
        self.llm_config = llm_config or LLMConfig()
        self.model = ChatModel()
        self.max_sample_rows = 50  # Limit rows sent to LLM to manage context

    async def execute(
        self,
        sql_generation: SQLGeneration,
        query_results: list[dict],
        user_prompt: str,
        database_connection: Any = None,
        language: str = "id",
    ) -> AnalysisResult:
        """Execute analysis on SQL query results.

        Args:
            sql_generation: The SQL generation record
            query_results: List of row dictionaries from query execution
            user_prompt: Original user question
            database_connection: Optional database connection for model config
            language: Response language ('id' for Indonesian, 'en' for English)

        Returns:
            AnalysisResult with summary, insights, and chart recommendations
        """
        start_time = datetime.now()

        # Initialize result
        result = AnalysisResult(
            sql_generation_id=sql_generation.id,
            prompt_id=sql_generation.prompt_id,
            llm_config=self.llm_config,
            row_count=len(query_results),
            column_count=len(query_results[0]) if query_results else 0,
        )

        try:
            # Get LLM
            llm = self.model.get_model(
                database_connection=database_connection,
                temperature=0.1,  # Slightly creative for insights
                model_family=self.llm_config.model_family,
                model_name=self.llm_config.model_name,
                api_base=self.llm_config.api_base,
            )

            # Prepare data sample for LLM
            columns = list(query_results[0].keys()) if query_results else []
            sample_size = min(len(query_results), self.max_sample_rows)
            data_sample = self._format_data_sample(query_results[:sample_size])

            # Build prompt with language-aware system prompt
            system_prompt = get_analysis_system_prompt(language)
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", ANALYSIS_USER_TEMPLATE),
            ])

            # Execute with token tracking
            with get_openai_callback() as cb:
                chain = prompt | llm
                response = await chain.ainvoke({
                    "user_prompt": user_prompt,
                    "sql_query": sql_generation.sql or "",
                    "row_count": len(query_results),
                    "columns": ", ".join(columns),
                    "sample_size": sample_size,
                    "data_sample": data_sample,
                })

                result.input_tokens_used = cb.prompt_tokens
                result.output_tokens_used = cb.completion_tokens

            # Parse response
            analysis_data = self._parse_llm_response(response.content)

            result.summary = analysis_data.get("summary", "Unable to generate summary.")
            result.insights = [
                Insight(**insight) for insight in analysis_data.get("insights", [])
            ]
            result.chart_recommendations = [
                ChartRecommendation(**rec)
                for rec in analysis_data.get("chart_recommendations", [])
            ]
            result.completed_at = datetime.now().isoformat()

        except Exception as e:
            logger.exception("Analysis generation failed")
            result.error = str(e)
            result.summary = f"Analysis failed: {str(e)}"
            result.completed_at = datetime.now().isoformat()

        return result

    def _format_data_sample(self, rows: list[dict]) -> str:
        """Format data rows for LLM consumption."""
        if not rows:
            return "No data returned."

        # Format as readable table
        lines = []
        for i, row in enumerate(rows):
            row_str = " | ".join(f"{k}: {self._format_value(v)}" for k, v in row.items())
            lines.append(f"Row {i + 1}: {row_str}")

        return "\n".join(lines)

    def _format_value(self, value: Any) -> str:
        """Format a single value for display."""
        if value is None:
            return "NULL"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str) and len(value) > 100:
            return value[:100] + "..."
        return str(value)

    def _parse_llm_response(self, content: str) -> dict:
        """Parse LLM response into structured analysis data."""
        try:
            # Try to extract JSON from markdown code block
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON object directly
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]

            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Return a fallback structure
            return {
                "summary": content[:500] if content else "Unable to generate summary.",
                "insights": [],
                "chart_recommendations": [],
            }

