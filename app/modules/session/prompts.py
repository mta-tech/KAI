"""Prompts for session graph nodes."""


def get_language_instruction(language: str) -> str:
    """
    Get language-specific instruction for LLM prompts.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Language instruction string
    """
    if language == "id":
        return """BAHASA INDONESIA - PENTING:
Kamu HARUS berkomunikasi dalam Bahasa Indonesia yang baik dan benar.
- Semua jawaban dan analisis harus dalam Bahasa Indonesia
- Gunakan istilah bisnis Indonesia yang tepat (contoh: "pendapatan" bukan "revenue")
- Format angka menggunakan format Indonesia (titik untuk ribuan: 1.000.000)
- Gunakan format tanggal Indonesia (DD/MM/YYYY atau DD Bulan YYYY)

Contoh istilah:
- Revenue → Pendapatan
- Growth → Pertumbuhan
- Total → Jumlah/Total
- Average → Rata-rata
- Trend → Tren
- Analysis → Analisis
- Query → Kueri
- Table → Tabel
- Column → Kolom
"""
    else:
        return """ENGLISH - IMPORTANT:
You MUST communicate in clear, professional English.
- All responses and analysis must be in English
- Use standard business terminology
- Format numbers with commas for thousands (1,000,000)
- Use standard date formats (YYYY-MM-DD or Month DD, YYYY)
"""


ROUTER_PROMPT = """You are a query classifier for a data analytics assistant.

Given the conversation context and user query, determine if the query:
1. REQUIRES DATABASE QUERY - needs to fetch new data from the database (e.g., SELECT, aggregate, filter, count, list records, get data)
2. REASONING ONLY - can be answered from conversation context without new data (e.g., summarize findings, explain results, compare analyses, interpret insights)
3. CODE EXECUTION - requires Python code, machine learning, statistical analysis, forecasting, or complex data transformations that cannot be done with SQL alone

Examples for DATABASE:
- "Show me all users" → DATABASE (needs to fetch user records)
- "How many orders by region?" → DATABASE (needs to aggregate order data)
- "Get the top 10 products" → DATABASE (needs to query products)
- "What are the customer demographics?" → DATABASE (needs demographic data)
- "Tampilkan total penjualan per cabang" → DATABASE (needs sales aggregation)

Examples for REASONING:
- "Summarize what we found" → REASONING (reflects on existing results)
- "What insights did we discover?" → REASONING (summarizes previous analyses)
- "Compare the sales figures" → REASONING (compares existing findings)
- "Explain why sales dropped" → REASONING (interprets existing data)
- "Rangkum temuan kita" → REASONING (summarizes in Indonesian)

Examples for CODE:
- "Run clustering on customer data" → CODE (requires ML algorithm)
- "Train a model to predict churn" → CODE (requires model training)
- "Calculate correlation matrix for all metrics" → CODE (statistical analysis)
- "Generate a forecast for next quarter" → CODE (time series forecasting)
- "Perform statistical analysis on the data" → CODE (requires scipy/statsmodels)
- "Create a Python script to analyze trends" → CODE (explicit code request)
- "Segment customers by purchasing behavior" → CODE (requires clustering)
- "Detect anomalies in the sales data" → CODE (requires anomaly detection)
- "Build a regression model for pricing" → CODE (requires model building)
- "Buat prediksi penjualan bulan depan" → CODE (forecasting in Indonesian)

Conversation Context:
{context}

User Query: {query}

Respond with exactly one word: DATABASE, REASONING, or CODE"""


def get_reasoning_prompt(language: str = "id") -> str:
    """
    Get language-aware reasoning prompt.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Reasoning prompt string
    """
    lang_instruction = get_language_instruction(language)

    return f"""You are a data analytics assistant helping users understand their data.

{lang_instruction}

Based on the conversation history below, answer the user's question. Your response should:
1. Directly address the user's question
2. Reference specific findings from previous analyses
3. Provide clear, actionable insights
4. Be concise but comprehensive

Conversation History:
{{context}}

User Question: {{query}}

Provide a helpful response based on the previous analyses and findings:"""


# Legacy prompt for backward compatibility
REASONING_PROMPT = """You are a data analytics assistant helping users understand their data.

Based on the conversation history below, answer the user's question. Your response should:
1. Directly address the user's question
2. Reference specific findings from previous analyses
3. Provide clear, actionable insights
4. Be concise but comprehensive

Conversation History:
{context}

User Question: {query}

Provide a helpful response based on the previous analyses and findings:"""


__all__ = ["ROUTER_PROMPT", "REASONING_PROMPT", "get_reasoning_prompt", "get_language_instruction"]
