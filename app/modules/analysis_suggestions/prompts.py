"""LLM prompts for analysis suggestion generation."""

SUGGESTION_GENERATION_SYSTEM_PROMPT = """You are a data analyst assistant helping users explore a database.
Your task is to generate insightful analysis questions that would be valuable for business users.

You must return a valid JSON array with the exact format specified. No additional text outside the JSON."""

SUGGESTION_GENERATION_USER_PROMPT = """Given this database schema, generate exactly {num_suggestions} insightful analysis questions.

## Database Schema

### Tables:
{tables_info}

### Relationships:
{relationships_info}

### Sample Data:
{sample_data}

## Requirements:
1. Generate exactly {num_suggestions} questions
2. Include a mix of categories:
   - "trend" - Time-based analysis (how metrics change over time)
   - "aggregation" - Summary statistics (totals, averages, counts, distributions)
   - "comparison" - Compare values across categories or groups
   - "relationship" - Explore connections between tables
3. Use natural business language that non-technical users can understand
4. Make questions specific to the actual data (use real column names and sample values when relevant)
5. Vary complexity: include some simple questions and some more complex ones

## Output Format:
Return ONLY a JSON array with this exact structure (no other text):
[
  {{
    "question": "Natural language question here",
    "category": "trend|aggregation|comparison|relationship",
    "rationale": "Brief explanation of why this is useful",
    "tables_involved": ["table1", "table2"],
    "columns_involved": ["col1", "col2"],
    "complexity": "simple|moderate|complex"
  }}
]"""

SUGGESTION_FALLBACK_TEMPLATES = {
    "trend": [
        "How has {metric} changed over time?",
        "Show the trend of {metric} by {time_column}",
        "What is the monthly distribution of records?",
    ],
    "aggregation": [
        "What is the total and average {metric}?",
        "Show the distribution of {metric} by {category}",
        "How many records are there per {category}?",
    ],
    "comparison": [
        "Compare {metric} across different {category} values",
        "Which {category} has the highest {metric}?",
        "Show the top 10 {category} by {metric}",
    ],
    "relationship": [
        "How do {table1} and {table2} relate to each other?",
        "Show {table1} with their associated {table2}",
        "What is the breakdown of {table2} per {table1}?",
    ],
}
