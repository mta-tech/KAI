"""Prompts for session graph nodes."""

ROUTER_PROMPT = """You are a query classifier for a data analytics assistant.

Given the conversation context and user query, determine if the query:
1. REQUIRES DATABASE QUERY - needs to fetch new data from the database (e.g., SELECT, aggregate, filter, count, list records, get data)
2. REASONING ONLY - can be answered from conversation context without new data (e.g., summarize findings, explain results, compare analyses, interpret insights)

Examples:
- "Show me all users" → DATABASE (needs to fetch user records)
- "Summarize what we found" → REASONING (reflects on existing results)
- "How many orders by region?" → DATABASE (needs to aggregate order data)
- "What insights did we discover?" → REASONING (summarizes previous analyses)
- "Compare the sales figures" → REASONING (compares existing findings)
- "Get the top 10 products" → DATABASE (needs to query products)
- "Explain why sales dropped" → REASONING (interprets existing data)
- "What are the customer demographics?" → DATABASE (needs demographic data)

Conversation Context:
{context}

User Query: {query}

Respond with exactly one word: DATABASE or REASONING"""


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


__all__ = ["ROUTER_PROMPT", "REASONING_PROMPT"]
