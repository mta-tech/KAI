"""Session module constants."""


def get_status_messages(language: str = "id") -> dict[str, str]:
    """Get language-aware status messages.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Dict of status messages
    """
    if language == "id":
        return {
            "build_context": "Memuat riwayat percakapan...",
            "route_query": "Menganalisis pertanyaan Anda...",
            "process_query": "Memproses pertanyaan Anda...",
            "reasoning_only": "Memikirkan pertanyaan Anda...",
            "code_execution": "Menjalankan analisis dengan kode Python...",
            "generate_sql": "Membuat kueri SQL...",
            "execute_sql": "Menjalankan kueri...",
            "generate_analysis": "Menghasilkan wawasan...",
            "summarize": "Memperbarui memori percakapan...",
            "save_checkpoint": "Menyimpan status sesi...",
            "save_message": "Menyimpan respons...",
        }
    else:
        return {
            "build_context": "Loading conversation history...",
            "route_query": "Analyzing your question...",
            "process_query": "Processing your question...",
            "reasoning_only": "Thinking about your question...",
            "code_execution": "Executing analysis with Python code...",
            "generate_sql": "Generating SQL query...",
            "execute_sql": "Running query...",
            "generate_analysis": "Generating insights...",
            "summarize": "Updating conversation memory...",
            "save_checkpoint": "Saving session state...",
            "save_message": "Saving response...",
        }


def get_thinking_traces(language: str = "id") -> dict[str, list[str]]:
    """Get language-aware thinking traces.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Dict of thinking trace lists
    """
    if language == "id":
        return {
            "build_context": [
                "Memuat konteks percakapan sebelumnya",
                "Memeriksa apakah pertanyaan terkait pernah ditanyakan sebelumnya",
            ],
            "route_query": [
                "Menentukan apakah ini memerlukan akses database atau dapat dijawab dari konteks",
            ],
            "process_query": [
                "Memahami maksud pertanyaan",
                "Membuat kueri SQL dari bahasa alami",
                "Menjalankan kueri ke database",
                "Menganalisis hasil dan menghasilkan wawasan",
            ],
            "reasoning_only": [
                "Menjawab dari konteks percakapan sebelumnya",
                "Tidak memerlukan kueri database",
            ],
            "code_execution": [
                "Mendeteksi kebutuhan analisis lanjutan (ML, statistik, forecasting)",
                "Mengalihkan ke autonomous agent untuk eksekusi kode Python",
                "Menjalankan model machine learning atau analisis statistik",
                "Menghasilkan wawasan dan visualisasi dari kode",
            ],
        }
    else:
        return {
            "build_context": [
                "Loading previous conversation context",
                "Checking if related questions were asked before",
            ],
            "route_query": [
                "Determining if this needs database access or can be answered from context",
            ],
            "process_query": [
                "Understanding the question intent",
                "Building SQL query from natural language",
                "Executing query against database",
                "Analyzing results and generating insights",
            ],
            "reasoning_only": [
                "Answering from previous conversation context",
                "No database query needed",
            ],
            "code_execution": [
                "Detecting need for advanced analysis (ML, statistics, forecasting)",
                "Routing to autonomous agent for Python code execution",
                "Running machine learning models or statistical analysis",
                "Generating insights and visualizations from code",
            ],
        }


# Legacy constants for backward compatibility
STATUS_MESSAGES = get_status_messages("en")
THINKING_TRACES = get_thinking_traces("en")

# Summarization thresholds
MAX_FULL_MESSAGES = 3  # Keep last N messages in full
SUMMARIZE_THRESHOLD_MESSAGES = 5  # Trigger summarization when messages exceed this
SUMMARIZE_THRESHOLD_TOKENS = 2000  # Or when token count exceeds this
MAX_SUMMARY_TOKENS = 500  # Maximum tokens for summary

# Session configuration
SESSION_COLLECTION_NAME = "sessions"
DEFAULT_SESSION_TTL_HOURS = 24

# Summarization prompt
SUMMARIZATION_PROMPT = """Given the conversation history below, create a concise summary that captures:
1. Key questions asked and their intent
2. Important findings/insights discovered
3. Any constraints or filters the user specified
4. SQL patterns that worked well

Keep the summary under {max_tokens} tokens.

Conversation history:
{history}

Summary:"""

__all__ = [
    "get_status_messages",
    "get_thinking_traces",
    "STATUS_MESSAGES",
    "THINKING_TRACES",
    "MAX_FULL_MESSAGES",
    "SUMMARIZE_THRESHOLD_MESSAGES",
    "SUMMARIZE_THRESHOLD_TOKENS",
    "MAX_SUMMARY_TOKENS",
    "SESSION_COLLECTION_NAME",
    "DEFAULT_SESSION_TTL_HOURS",
    "SUMMARIZATION_PROMPT",
]
