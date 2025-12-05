"""Session module constants."""

# Status messages for SSE streaming
STATUS_MESSAGES = {
    "build_context": "Loading conversation history...",
    "route_query": "Analyzing your question...",
    "process_query": "Processing your question...",
    "reasoning_only": "Thinking about your question...",
    "generate_sql": "Generating SQL query...",
    "execute_sql": "Running query...",
    "generate_analysis": "Generating insights...",
    "summarize": "Updating conversation memory...",
    "save_checkpoint": "Saving session state...",
    "save_message": "Saving response...",
}

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
    "STATUS_MESSAGES",
    "MAX_FULL_MESSAGES",
    "SUMMARIZE_THRESHOLD_MESSAGES",
    "SUMMARIZE_THRESHOLD_TOKENS",
    "MAX_SUMMARY_TOKENS",
    "SESSION_COLLECTION_NAME",
    "DEFAULT_SESSION_TTL_HOURS",
    "SUMMARIZATION_PROMPT",
]
