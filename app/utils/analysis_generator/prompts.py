"""Prompts for comprehensive analysis generation."""


def get_language_instruction(language: str) -> str:
    """Get language-specific instruction for analysis prompts.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Language instruction string
    """
    if language == "id":
        return """BAHASA INDONESIA - PENTING:
Kamu HARUS memberikan analisis dalam Bahasa Indonesia yang baik dan benar.
- Semua summary, insights, dan rekomendasi harus dalam Bahasa Indonesia
- Gunakan istilah bisnis Indonesia yang tepat
- Format angka menggunakan format Indonesia (titik untuk ribuan: 1.000.000)
- Gunakan format tanggal Indonesia (DD/MM/YYYY atau DD Bulan YYYY)

Contoh istilah:
- Revenue → Pendapatan
- Growth → Pertumbuhan
- Average → Rata-rata
- Trend → Tren
- Analysis → Analisis
- Insight → Temuan/Wawasan
- Summary → Ringkasan
"""
    else:
        return """ENGLISH - IMPORTANT:
You MUST provide analysis in clear, professional English.
- All summaries, insights, and recommendations must be in English
- Use standard business terminology
- Format numbers with commas for thousands (1,000,000)
- Use standard date formats (YYYY-MM-DD or Month DD, YYYY)
"""


def get_analysis_system_prompt(language: str = "id") -> str:
    """Get language-aware analysis system prompt.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        System prompt string
    """
    lang_instruction = get_language_instruction(language)

    return f"""You are an expert data analyst. Your task is to analyze SQL query results and provide comprehensive insights.

{lang_instruction}

Given a user's question, the SQL query that was executed, and the query results, you must provide:

1. **Summary**: A clear, concise natural language summary of what the data shows, directly answering the user's question.

2. **Insights**: Key patterns, trends, anomalies, or notable findings in the data. Each insight should have:
   - A clear title
   - A description explaining the insight
   - Significance level (high/medium/low)
   - Supporting data points if relevant

3. **Chart Recommendations**: Suggest the best ways to visualize this data. For each recommendation:
   - Chart type (bar, line, pie, scatter, table, heatmap, etc.)
   - Title for the visualization
   - Description of what it would show
   - Which columns to use for axes/dimensions
   - Why this visualization is appropriate

Be specific and actionable. Focus on insights that would be valuable to a business user.
"""


# Legacy constant for backward compatibility
ANALYSIS_SYSTEM_PROMPT = get_analysis_system_prompt("en")

ANALYSIS_USER_TEMPLATE = """## User Question
{user_prompt}

## SQL Query Executed
```sql
{sql_query}
```

## Query Results
Row count: {row_count}
Columns: {columns}

Data (first {sample_size} rows):
{data_sample}

## Your Analysis

Provide a comprehensive analysis with:
1. A natural language summary answering the user's question
2. Key insights found in the data (at least 2-3 if the data supports it)
3. Chart/visualization recommendations (at least 1-2 appropriate visualizations)

Respond in the following JSON format:
```json
{{
    "summary": "Your summary here...",
    "insights": [
        {{
            "title": "Insight title",
            "description": "Detailed description",
            "significance": "high|medium|low",
            "data_points": [...]
        }}
    ],
    "chart_recommendations": [
        {{
            "chart_type": "bar|line|pie|scatter|table|heatmap",
            "title": "Chart title",
            "description": "What this chart shows",
            "x_axis": "column_name",
            "y_axis": "column_name",
            "columns": ["col1", "col2"],
            "rationale": "Why this visualization"
        }}
    ]
}}
```
"""

