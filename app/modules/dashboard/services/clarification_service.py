"""LLM-based dashboard clarification question generation service."""
from __future__ import annotations

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.data.db.storage import Storage
from app.modules.dashboard.models import (
    ClarificationOption,
    ClarificationQuestion,
    ClarificationResponse,
)
from app.modules.mdl.repositories import MDLRepository
from app.modules.sql_generation.models import LLMConfig
from app.modules.table_description.repositories import TableDescriptionRepository
from app.server.config import Settings
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)

CLARIFICATION_SYSTEM_PROMPT = """You are an expert BI analyst helping users create dashboards. Your task is to generate exactly 3 clarification questions to better understand the user's dashboard requirements.

Each question should have exactly 3 answer options that are specific to the available data schema.

Return your response as valid JSON in this exact format:
{
  "questions": [
    {
      "question": "What specific metrics should this dashboard focus on?",
      "options": [
        {"label": "Option 1", "description": "Brief explanation of this option"},
        {"label": "Option 2", "description": "Brief explanation of this option"},
        {"label": "Option 3", "description": "Brief explanation of this option"}
      ]
    }
  ]
}

Rules:
- Generate exactly 3 questions
- Each question must have exactly 3 options
- Options should be specific to the actual columns and tables in the schema
- Use actual column names, table names, and business context
- Questions should cover: metrics focus, time granularity, and data dimensions
- Keep option labels concise (2-5 words)
- Keep descriptions brief (under 50 characters)"""

CLARIFICATION_USER_PROMPT = """Generate 3 clarification questions for this dashboard request.

## User Request
{user_request}

## Database Schema
{schema_info}

## Available Tables
{table_names}

## Sample Data
{sample_data}

Generate questions that help clarify:
1. What specific metrics or KPIs to focus on
2. What time granularity or period to use
3. What dimensions to break down data by

Return valid JSON with exactly 3 questions, each with 3 options."""


class ClarificationService:
    """LLM-based clarification question generation."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.mdl_repo = MDLRepository(storage)
        self.table_repo = TableDescriptionRepository(storage)
        self.settings = Settings()

    async def generate_clarifications(
        self,
        user_request: str,
        db_connection_id: str,
        llm_config: Optional[LLMConfig] = None,
    ) -> ClarificationResponse:
        """
        Generate clarification questions based on schema and user request.

        Args:
            user_request: Natural language dashboard description
            db_connection_id: Database connection ID
            llm_config: Optional LLM configuration

        Returns:
            ClarificationResponse with list of questions
        """
        # Build context
        context = await self._build_context(db_connection_id)

        # Get LLM
        llm = self._get_llm(llm_config)

        # Format prompt
        user_prompt = CLARIFICATION_USER_PROMPT.format(
            user_request=user_request,
            schema_info=context["schema_info"],
            table_names=context["table_names"],
            sample_data=context["sample_data"],
        )

        # Call LLM
        messages = [
            SystemMessage(content=CLARIFICATION_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await llm.ainvoke(messages)
            return self._parse_response(response.content)
        except Exception as e:
            logger.error(f"Clarification generation failed: {e}")
            # Return fallback questions
            return self._create_fallback_questions()

    async def _build_context(self, db_connection_id: str) -> dict:
        """Build context from database schema."""
        table_descriptions = self.table_repo.find_by(
            {"db_connection_id": db_connection_id}
        )

        schema_lines = []
        table_names = []
        sample_data_lines = []

        for table in table_descriptions:
            table_names.append(table.table_name)
            columns = []

            for col in table.columns:
                col_info = f"  - {col.name} ({col.data_type})"
                if col.description:
                    col_info += f": {col.description}"
                columns.append(col_info)

            schema_lines.append(f"**{table.table_name}**")
            if table.table_description:
                schema_lines.append(f"  Description: {table.table_description}")
            schema_lines.append("  Columns:")
            schema_lines.extend(columns)
            schema_lines.append("")

            # Add sample data
            if table.examples:
                sample_data_lines.append(f"**{table.table_name}** samples:")
                for i, row in enumerate(table.examples[:2]):
                    sample_data_lines.append(
                        f"  Row {i+1}: {json.dumps(row, default=str)}"
                    )

        return {
            "schema_info": "\n".join(schema_lines) or "No schema information available",
            "table_names": ", ".join(table_names) or "No tables found",
            "sample_data": "\n".join(sample_data_lines) or "No sample data available",
        }

    def _get_llm(self, llm_config: Optional[LLMConfig]):
        """Get LLM instance."""
        if llm_config:
            model_family = llm_config.model_family
            model_name = llm_config.model_name
        else:
            model_family = self.settings.CHAT_FAMILY or "google"
            model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"

        return ChatModel().get_model(
            database_connection=None,
            model_family=model_family,
            model_name=model_name,
            temperature=0.3,
        )

    def _parse_response(self, content: str) -> ClarificationResponse:
        """Parse LLM response into ClarificationResponse."""
        try:
            # Clean response
            content = content.strip()

            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)

            questions = []
            for q in data.get("questions", []):
                options = [
                    ClarificationOption(
                        label=opt.get("label", ""),
                        description=opt.get("description", ""),
                    )
                    for opt in q.get("options", [])
                ]
                questions.append(
                    ClarificationQuestion(
                        question=q.get("question", ""),
                        options=options,
                        allow_custom=True,
                    )
                )

            return ClarificationResponse(questions=questions)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clarification response: {e}")
            return self._create_fallback_questions()

    def _create_fallback_questions(self) -> ClarificationResponse:
        """Create fallback questions if LLM fails."""
        return ClarificationResponse(
            questions=[
                ClarificationQuestion(
                    question="What is the primary purpose of this dashboard?",
                    options=[
                        ClarificationOption(
                            label="Monitoring",
                            description="Track real-time metrics and KPIs",
                        ),
                        ClarificationOption(
                            label="Reporting",
                            description="Generate periodic business reports",
                        ),
                        ClarificationOption(
                            label="Analysis",
                            description="Deep-dive into data patterns",
                        ),
                    ],
                ),
                ClarificationQuestion(
                    question="What metrics matter most?",
                    options=[
                        ClarificationOption(
                            label="Revenue",
                            description="Sales, income, financial metrics",
                        ),
                        ClarificationOption(
                            label="Volume",
                            description="Counts, quantities, transactions",
                        ),
                        ClarificationOption(
                            label="Performance",
                            description="Efficiency, trends, comparisons",
                        ),
                    ],
                ),
                ClarificationQuestion(
                    question="What time period should the dashboard cover?",
                    options=[
                        ClarificationOption(
                            label="Daily",
                            description="Day-over-day analysis",
                        ),
                        ClarificationOption(
                            label="Weekly",
                            description="Week-over-week trends",
                        ),
                        ClarificationOption(
                            label="Monthly",
                            description="Month-over-month reports",
                        ),
                    ],
                ),
            ]
        )


__all__ = ["ClarificationService"]
