"""Follow-up question and exploration suggestion tools."""
import json
import pandas as pd


def create_suggestions_tool():
    """Create follow-up question suggestion tool."""

    def suggest_questions(
        data_json: str,
        original_question: str,
        columns_used: list[str] | None = None,
    ) -> str:
        """Suggest follow-up questions based on data and context.

        Args:
            data_json: JSON string of current data results
            original_question: The question that produced this data
            columns_used: Columns involved in the analysis

        Returns:
            JSON with suggested follow-up questions
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)
            suggestions = []

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            all_cols = numeric_cols + cat_cols

            # 1. Drill-down suggestions
            for col in cat_cols[:2]:
                unique_values = df[col].nunique()
                if unique_values > 1 and unique_values < 20:
                    top_value = df[col].value_counts().index[0]
                    suggestions.append({
                        "question": f"Show me details for {col} = '{top_value}'",
                        "category": "drill_down",
                        "rationale": f"Drill into the most common {col} value"
                    })

            # 2. Comparison suggestions
            if len(cat_cols) >= 2:
                suggestions.append({
                    "question": f"Compare {numeric_cols[0] if numeric_cols else 'values'} across different {cat_cols[0]}",
                    "category": "compare",
                    "rationale": "Compare performance across categories"
                })

            # 3. Trend suggestions
            if len(numeric_cols) > 0:
                suggestions.append({
                    "question": f"Show me the trend of {numeric_cols[0]} over time",
                    "category": "trend",
                    "rationale": "Understand how values change over time"
                })

            # 4. Filter suggestions
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                median = df[col].median()
                suggestions.append({
                    "question": f"Show only records where {col} is above {median:.2f}",
                    "category": "filter",
                    "rationale": "Focus on above-average performers"
                })

            # 5. Aggregation suggestions
            if len(cat_cols) > 0 and len(numeric_cols) > 0:
                suggestions.append({
                    "question": f"What is the total and average {numeric_cols[0]} by {cat_cols[0]}?",
                    "category": "aggregate",
                    "rationale": "Summarize metrics by category"
                })

            # 6. Context-aware suggestions based on original question
            if "top" in original_question.lower() or "best" in original_question.lower():
                suggestions.append({
                    "question": "Now show me the bottom performers",
                    "category": "compare",
                    "rationale": "Compare with worst performers"
                })

            if "total" in original_question.lower() or "sum" in original_question.lower():
                suggestions.append({
                    "question": "Break this down by month",
                    "category": "drill_down",
                    "rationale": "See temporal distribution"
                })

            return json.dumps({
                "success": True,
                "suggestion_count": len(suggestions),
                "suggestions": suggestions[:5]  # Return top 5
            })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return suggest_questions
