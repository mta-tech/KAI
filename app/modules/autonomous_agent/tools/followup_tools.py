"""LLM-powered follow-up question suggestion tool."""
import json
import logging

from app.modules.database_connection.models import DatabaseConnection
from app.data.db.storage import Storage

logger = logging.getLogger(__name__)


def create_suggest_follow_ups_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create LLM-powered follow-up question suggestion tool.

    Uses an LLM call to generate contextually relevant follow-up questions
    based on the original question and analysis summary.
    """

    def suggest_follow_ups(
        original_question: str,
        analysis_summary: str,
        data_columns: list[str] | None = None,
    ) -> str:
        """Suggest 3-5 contextually relevant follow-up questions using AI.

        Call this after completing analysis to generate insightful follow-up
        questions the user might want to explore next.

        Args:
            original_question: The user's original question that was analyzed
            analysis_summary: A brief summary of the analysis findings
            data_columns: Optional list of column names in the result data

        Returns:
            JSON with suggested follow-up questions, each with question,
            category (drill_down/compare/trend/filter/aggregate), and rationale
        """
        try:
            from app.utils.model.chat_model import ChatModel
            from app.server.config import get_settings  # type: ignore[attr-defined]

            settings = get_settings()
            chat_model = ChatModel()
            llm = chat_model.get_model(
                database_connection=db_connection,
                temperature=0,
                model_family=settings.CHAT_FAMILY or "google",
                model_name=settings.CHAT_MODEL or "gemini-2.0-flash",
            )

            columns_context = ""
            if data_columns:
                columns_context = f"\nAvailable data columns: {', '.join(data_columns)}"

            prompt = (
                "You are a data analysis assistant. Generate 3-5 insightful follow-up questions "
                "that would help the user explore the data further. "
                "Each question must belong to exactly one of these categories:\n"
                "- drill_down: Dig deeper into a specific subset or dimension\n"
                "- compare: Compare different groups, periods, or metrics\n"
                "- trend: Understand how values change over time\n"
                "- filter: Focus on records meeting specific criteria\n"
                "- aggregate: Summarize or group data differently\n\n"
                "Respond ONLY with a valid JSON object in this exact format:\n"
                '{"questions": [{"question": "...", "category": "...", "rationale": "..."}, ...]}\n\n'
                f"Original question: {original_question}\n"
                f"Analysis summary: {analysis_summary}"
                f"{columns_context}\n\n"
                "Generate 3-5 follow-up questions."
            )

            response = llm.invoke(prompt)

            raw_content = response.content if hasattr(response, "content") else str(response)
            content = raw_content if isinstance(raw_content, str) else str(raw_content)
            content = content.strip()
            # Strip markdown code fences if present
            if content.startswith("```"):
                lines = content.splitlines()
                content = "\n".join(
                    line for line in lines
                    if not line.startswith("```")
                ).strip()

            parsed = json.loads(content)
            questions = parsed.get("questions", [])

            valid_categories = {"drill_down", "compare", "trend", "filter", "aggregate"}
            validated = []
            for q in questions:
                category = q.get("category", "drill_down")
                if category not in valid_categories:
                    category = "drill_down"
                validated.append({
                    "question": q.get("question", ""),
                    "category": category,
                    "rationale": q.get("rationale", ""),
                })

            return json.dumps({
                "success": True,
                "questions": validated[:5],
            })

        except Exception as e:
            logger.warning(f"suggest_follow_ups failed: {e}")
            return json.dumps({"success": False, "error": str(e), "questions": []})

    return suggest_follow_ups
