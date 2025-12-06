"""Analysis suggestion generation service."""
import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.data.db.storage import Storage
from app.modules.mdl.models import MDLManifest
from app.modules.mdl.repositories import MDLRepository
from app.modules.table_description.models import TableDescription
from app.modules.table_description.repositories import TableDescriptionRepository
from app.modules.sql_generation.models import LLMConfig
from app.modules.analysis_suggestions.models import (
    AnalysisSuggestion,
    AnalysisSuggestionsResponse,
    SuggestionCategory,
)
from app.modules.analysis_suggestions.prompts import (
    SUGGESTION_GENERATION_SYSTEM_PROMPT,
    SUGGESTION_GENERATION_USER_PROMPT,
    SUGGESTION_FALLBACK_TEMPLATES,
)
from app.server.config import Settings
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)


class AnalysisSuggestionService:
    """Service for generating analysis suggestions based on MDL and sample data."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.mdl_repo = MDLRepository(storage)
        self.table_repo = TableDescriptionRepository(storage)
        self.settings = Settings()

    async def generate_suggestions(
        self,
        db_connection_id: str,
        max_suggestions: int = 8,
        llm_config: Optional[LLMConfig] = None,
    ) -> AnalysisSuggestionsResponse:
        """
        Generate analysis suggestions based on MDL and sample data.

        Args:
            db_connection_id: Database connection ID
            max_suggestions: Maximum number of suggestions to return
            llm_config: Optional LLM configuration (uses default from settings if not provided)

        Returns:
            AnalysisSuggestionsResponse with generated suggestions
        """
        # Fetch MDL manifest
        manifest = await self.mdl_repo.get_by_db_connection(db_connection_id)

        # Fetch table descriptions with sample data
        table_descriptions = self.table_repo.find_by(
            {"db_connection_id": db_connection_id}
        )

        if not table_descriptions:
            return AnalysisSuggestionsResponse(
                db_connection_id=db_connection_id,
                suggestions=[],
                mdl_available=manifest is not None,
                table_count=0,
                relationship_count=0,
            )

        # Build schema context
        schema_context = self._build_schema_context(manifest, table_descriptions)

        # Try LLM-based generation first
        suggestions = await self._generate_with_llm(
            schema_context=schema_context,
            max_suggestions=max_suggestions,
            llm_config=llm_config,
        )

        # Fall back to rule-based if LLM fails
        if not suggestions:
            logger.info("LLM suggestion generation failed, using fallback")
            suggestions = self._generate_fallback_suggestions(
                manifest=manifest,
                table_descriptions=table_descriptions,
                max_suggestions=max_suggestions,
            )

        return AnalysisSuggestionsResponse(
            db_connection_id=db_connection_id,
            suggestions=suggestions,
            mdl_available=manifest is not None,
            table_count=len(table_descriptions),
            relationship_count=len(manifest.relationships) if manifest else 0,
        )

    def _build_schema_context(
        self,
        manifest: Optional[MDLManifest],
        table_descriptions: list[TableDescription],
    ) -> dict:
        """Build schema context for LLM prompt."""
        # Build tables info
        tables_info = []
        for table in table_descriptions:
            columns = []
            for col in table.columns:
                col_info = f"  - {col.name} ({col.data_type})"
                if col.description:
                    col_info += f": {col.description}"
                if col.is_primary_key:
                    col_info += " [PK]"
                if col.foreign_key:
                    col_info += f" [FK -> {col.foreign_key.reference_table}]"
                if col.low_cardinality and col.categories:
                    col_info += f" (values: {', '.join(str(c) for c in col.categories[:5])})"
                columns.append(col_info)

            table_info = f"**{table.table_name}**"
            if table.table_description:
                table_info += f"\n  Description: {table.table_description}"
            table_info += f"\n  Columns:\n" + "\n".join(columns)
            tables_info.append(table_info)

        # Build relationships info
        relationships_info = "No relationships defined"
        if manifest and manifest.relationships:
            rel_lines = []
            for rel in manifest.relationships:
                rel_lines.append(
                    f"- {rel.name}: {rel.models[0]} <-> {rel.models[1]} ({rel.join_type.value})"
                )
            relationships_info = "\n".join(rel_lines)

        # Build sample data
        sample_data_lines = []
        for table in table_descriptions[:5]:  # Limit to 5 tables
            if table.examples:
                sample_data_lines.append(f"**{table.table_name}** (sample rows):")
                for i, row in enumerate(table.examples[:2]):  # Limit to 2 rows
                    sample_data_lines.append(f"  Row {i+1}: {json.dumps(row, default=str)}")

        sample_data = "\n".join(sample_data_lines) if sample_data_lines else "No sample data available"

        return {
            "tables_info": "\n\n".join(tables_info),
            "relationships_info": relationships_info,
            "sample_data": sample_data,
        }

    async def _generate_with_llm(
        self,
        schema_context: dict,
        max_suggestions: int,
        llm_config: Optional[LLMConfig],
    ) -> list[AnalysisSuggestion]:
        """Generate suggestions using LLM."""
        try:
            # Get LLM config
            if llm_config:
                model_family = llm_config.model_family
                model_name = llm_config.model_name
            else:
                model_family = self.settings.CHAT_FAMILY or "google"
                model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"

            # Create LLM
            llm = ChatModel().get_model(
                database_connection=None,
                model_family=model_family,
                model_name=model_name,
                temperature=0.7,  # Some creativity for diverse suggestions
            )

            # Format prompt
            user_prompt = SUGGESTION_GENERATION_USER_PROMPT.format(
                num_suggestions=max_suggestions,
                tables_info=schema_context["tables_info"],
                relationships_info=schema_context["relationships_info"],
                sample_data=schema_context["sample_data"],
            )

            # Call LLM
            messages = [
                SystemMessage(content=SUGGESTION_GENERATION_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
            response = await llm.ainvoke(messages)

            # Parse response
            return self._parse_llm_response(response.content)

        except Exception as e:
            logger.warning(f"LLM suggestion generation failed: {e}")
            return []

    def _parse_llm_response(self, content: str) -> list[AnalysisSuggestion]:
        """Parse LLM response into AnalysisSuggestion objects."""
        try:
            # Try to extract JSON from response
            content = content.strip()

            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)

            suggestions = []
            for item in data:
                try:
                    # Validate category
                    category = item.get("category", "aggregation").lower()
                    if category not in [c.value for c in SuggestionCategory]:
                        category = "aggregation"

                    suggestions.append(AnalysisSuggestion(
                        question=item.get("question", ""),
                        category=SuggestionCategory(category),
                        rationale=item.get("rationale", ""),
                        tables_involved=item.get("tables_involved", []),
                        columns_involved=item.get("columns_involved", []),
                        complexity=item.get("complexity", "simple"),
                    ))
                except Exception as e:
                    logger.debug(f"Failed to parse suggestion item: {e}")
                    continue

            return suggestions

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return []

    def _generate_fallback_suggestions(
        self,
        manifest: Optional[MDLManifest],
        table_descriptions: list[TableDescription],
        max_suggestions: int,
    ) -> list[AnalysisSuggestion]:
        """Generate rule-based fallback suggestions."""
        suggestions = []

        # Analyze schema
        time_columns = []
        numeric_columns = []
        categorical_columns = []

        for table in table_descriptions:
            for col in table.columns:
                col_type = (col.data_type or "").lower()

                # Check for time columns
                if any(t in col_type for t in ["date", "time", "timestamp"]):
                    time_columns.append((table.table_name, col.name))

                # Check for numeric columns
                elif any(t in col_type for t in ["int", "float", "decimal", "numeric", "double", "real"]):
                    numeric_columns.append((table.table_name, col.name))

                # Check for categorical columns
                if col.low_cardinality and col.categories:
                    categorical_columns.append((table.table_name, col.name, col.categories))

        # Generate trend suggestions
        if time_columns and numeric_columns:
            time_table, time_col = time_columns[0]
            for table, num_col in numeric_columns[:2]:
                if table == time_table:
                    suggestions.append(AnalysisSuggestion(
                        question=f"How has {num_col} changed over time?",
                        category=SuggestionCategory.TREND,
                        rationale=f"Analyze trends in {num_col} using {time_col}",
                        tables_involved=[table],
                        columns_involved=[time_col, num_col],
                        complexity="simple",
                    ))

        # Generate aggregation suggestions
        for table, num_col in numeric_columns[:2]:
            cat_cols = [(t, c, cats) for t, c, cats in categorical_columns if t == table]
            if cat_cols:
                cat_col = cat_cols[0][1]
                suggestions.append(AnalysisSuggestion(
                    question=f"What is the total and average {num_col} by {cat_col}?",
                    category=SuggestionCategory.AGGREGATION,
                    rationale=f"Summarize {num_col} across different {cat_col} values",
                    tables_involved=[table],
                    columns_involved=[num_col, cat_col],
                    complexity="simple",
                ))

        # Generate comparison suggestions
        for table, cat_col, categories in categorical_columns[:2]:
            num_cols = [(t, c) for t, c in numeric_columns if t == table]
            if num_cols:
                num_col = num_cols[0][1]
                suggestions.append(AnalysisSuggestion(
                    question=f"Compare {num_col} across different {cat_col} values",
                    category=SuggestionCategory.COMPARISON,
                    rationale=f"Identify differences between {cat_col} categories",
                    tables_involved=[table],
                    columns_involved=[cat_col, num_col],
                    complexity="moderate",
                ))

        # Generate relationship suggestions from MDL
        if manifest and manifest.relationships:
            for rel in manifest.relationships[:2]:
                suggestions.append(AnalysisSuggestion(
                    question=f"How do {rel.models[0]} and {rel.models[1]} relate to each other?",
                    category=SuggestionCategory.RELATIONSHIP,
                    rationale=f"Explore the {rel.join_type.value} relationship",
                    tables_involved=rel.models,
                    columns_involved=[],
                    complexity="moderate",
                ))

        return suggestions[:max_suggestions]


__all__ = ["AnalysisSuggestionService"]
