#!/usr/bin/env python3
"""
KAI Cookbook - Basic 08: SQL Generation

This script demonstrates how to generate SQL from natural language prompts in KAI.
This is a core feature that converts text queries into executable SQL.

API Endpoints:
- POST /api/v1/prompts/{prompt_id}/sql-generations - Generate SQL from a prompt
- POST /api/v1/prompts/sql-generations - Create prompt and generate SQL in one call
- GET /api/v1/sql-generations - List SQL generations (filtered by prompt)
- GET /api/v1/sql-generations/{id} - Get a specific SQL generation
- PUT /api/v1/sql-generations/{id} - Update SQL generation metadata
- GET /api/v1/sql-generations/{id}/execute - Execute the generated SQL
- GET /api/v1/sql-generations/{id}/execute-store - Execute and store results as CSV

SQL Generation Options:
- llm_config: LLM provider and model to use
- using_ner: Use Named Entity Recognition for better accuracy
- evaluate: Evaluate the generated SQL
- sql: Provide custom SQL (optional, for manual override)
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    KAIAPIClient,
    SAMPLE_DB_ALIAS,
    print_section,
    print_subsection,
    print_response,
    press_to_continue,
    parse_cookbook_args,
)


def get_connection_id_by_alias(client: KAIAPIClient, alias: str) -> str | None:
    """Get connection ID by alias."""
    connections = client.get("/database-connections")
    for conn in connections:
        if conn.get("alias") == alias:
            return conn.get("id")
    return None


def get_or_create_prompt(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
) -> dict:
    """Get existing prompt or create new one."""
    prompts = client.get("/prompts", params={"db_connection_id": connection_id})
    for pr in prompts:
        if pr.get("text") == text:
            return pr

    # Create new prompt
    return client.post("/prompts", json_data={
        "text": text,
        "db_connection_id": connection_id,
        "metadata": {"created_by": "cookbook"}
    })


def create_sql_generation(
    client: KAIAPIClient,
    prompt_id: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    using_ner: bool = False,
    evaluate: bool = False,
) -> dict:
    """Generate SQL from a prompt."""
    print_subsection("Generating SQL from prompt")

    payload = {
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        },
        "using_ner": using_ner,
        "evaluate": evaluate,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  LLM: {llm_provider}/{llm_model}")
    print(f"  Using NER: {using_ner}")
    print(f"  Evaluate: {evaluate}")
    print("  Generating SQL...")

    sql_gen = client.post(f"/prompts/{prompt_id}/sql-generations", json_data=payload)

    print(f"  Status: {sql_gen['status']}")
    print(f"  SQL: {sql_gen.get('sql', 'N/A')}")

    if sql_gen.get('intermediate_steps'):
        print(f"  Steps: {len(sql_gen['intermediate_steps'])} intermediate steps")

    return sql_gen


def create_prompt_and_sql(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
) -> dict:
    """Create prompt and generate SQL in one call."""
    print_subsection("Creating prompt and generating SQL")

    payload = {
        "prompt": {
            "text": text,
            "db_connection_id": connection_id,
            "schemas": ["public"],
            "metadata": {"created_by": "cookbook"}
        },
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        },
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Prompt: {text}")
    print(f"  Generating SQL...")

    sql_gen = client.post("/prompts/sql-generations", json_data=payload)

    print(f"  Status: {sql_gen['status']}")
    print(f"  SQL: {sql_gen.get('sql', 'N/A')}")
    print(f"  Prompt ID: {sql_gen['prompt_id']}")

    return sql_gen


def get_sql_generation(client: KAIAPIClient, sql_gen_id: str) -> dict:
    """Get a specific SQL generation."""
    print_subsection(f"Getting SQL generation: {sql_gen_id}")
    sql_gen = client.get(f"/sql-generations/{sql_gen_id}")
    return sql_gen


def execute_sql(
    client: KAIAPIClient,
    sql_gen_id: str,
    max_rows: int = 100,
) -> list:
    """Execute a generated SQL query."""
    print_subsection(f"Executing SQL: {sql_gen_id}")

    print(f"  Max rows: {max_rows}")
    print("  Executing...")

    results = client.get(f"/sql-generations/{sql_gen_id}/execute", params={"max_rows": max_rows})

    if not results:
        print("  No results returned.")
        return []

    print(f"  ✓ Returned {len(results)} row(s)")

    # Show first few rows
    if results:
        headers = list(results[0].keys())
        print(f"\n  Columns: {', '.join(headers)}")

        print(f"\n  First 3 rows:")
        for i, row in enumerate(results[:3], 1):
            print(f"    Row {i}: {row}")

    return results


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 08: SQL Generation")

    client = KAIAPIClient()

    # Use sample database from environment
    example_alias = SAMPLE_DB_ALIAS
    print(f"\nUsing connection alias: {example_alias}")
    press_to_continue("Press Enter to continue or Ctrl+C to cancel...")

    # Step 1: Get the connection ID
    print("\n[Step 1] Get connection ID")
    connection_id = get_connection_id_by_alias(client, example_alias)

    if not connection_id:
        print(f"  ✗ Connection '{example_alias}' not found!")
        return

    print(f"  ✓ Found connection: {example_alias}")
    press_to_continue()

    # Step 2: Generate SQL from existing prompt
    print("\n[Step 2] Generate SQL from existing prompt")

    # First, create or get a prompt
    prompt = get_or_create_prompt(
        client,
        connection_id,
        "Show me the total sales for each month"
    )

    print(f"  Prompt: {prompt['text']}")
    print(f"  Prompt ID: {prompt['id']}")
    press_to_continue("Press Enter to generate SQL...")

    try:
        sql_gen = create_sql_generation(
            client,
            prompt["id"],
            llm_provider="google",
            llm_model="gemini-2.0-flash-exp",
            using_ner=True,
            evaluate=True
        )
        print_response(sql_gen, "Generated SQL")
    except Exception as e:
        print(f"  ! SQL generation failed: {e}")
        print("  Make sure LLM API keys are configured in the server")
        return
    press_to_continue()

    # Step 3: Create prompt and generate SQL in one call
    print("\n[Step 3] Create prompt and generate SQL (one call)")
    press_to_continue("Press Enter to continue...")

    try:
        sql_gen2 = create_prompt_and_sql(
            client,
            connection_id,
            "List the top 5 products by revenue",
            llm_provider="google",
            llm_model="gemini-2.0-flash-exp"
        )
        print_response(sql_gen2, "Generated SQL (one-call)")
    except Exception as e:
        print(f"  ! SQL generation failed: {e}")
    press_to_continue()

    # Step 4: Get SQL generation details
    print("\n[Step 4] Get SQL generation details")
    if sql_gen:
        details = get_sql_generation(client, sql_gen["id"])
        print(f"  Status: {details['status']}")
        print(f"  SQL: {details.get('sql', 'N/A')}")
        print(f"  Confidence: {details.get('confidence_score', 'N/A')}")

        if details.get('input_tokens_used'):
            print(f"  Input Tokens: {details['input_tokens_used']}")
        if details.get('output_tokens_used'):
            print(f"  Output Tokens: {details['output_tokens_used']}")
    press_to_continue()

    # Step 5: Execute generated SQL
    print("\n[Step 5] Execute generated SQL")
    if sql_gen:
        print("  Executing the SQL from Step 2...")
        press_to_continue("Press Enter to execute...")

        try:
            results = execute_sql(client, sql_gen["id"], max_rows=10)
            if results:
                print(f"\n  Full results (showing up to 10 rows):")
                for i, row in enumerate(results, 1):
                    print(f"    {i}. {row}")
        except Exception as e:
            print(f"  ! Execution failed: {e}")
            print("  This might be due to:")
            print("    - Database not running")
            print("    - Invalid table/column names in generated SQL")
            print("    - Schema mismatch")
    press_to_continue()

    # Step 6: List SQL generations for a prompt
    print("\n[Step 6] List SQL generations for a prompt")
    if prompt:
        sql_gens = client.get("/sql-generations", params={"prompt_id": prompt["id"]})
        print(f"  Found {len(sql_gens)} SQL generation(s) for this prompt")
        for sg in sql_gens:
            print(f"    - ID: {sg['id']}")
            print(f"      Status: {sg['status']}")
            print(f"      SQL: {sg.get('sql', 'N/A')[:50]}...")
    press_to_continue()

    # Step 7: Cleanup
    print("\n[Step 7] Summary")
    print("  SQL generations are stored for reference and execution.")
    print("  They can be re-executed or used as examples for context stores.")

    if should_cleanup:
        print("  --cleanup enabled: SQL generations will be preserved.")
        print("  (SQL generations are not typically deleted as they are reference material)")
    else:
        print("  --no-cleanup: Preserving created resources.")

    print_section("Demo Complete")
    print("\nNext Steps:")
    print("  - Generate natural language insights from SQL results (Basic 09)")
    print("  - Store results to CSV/GCS")
    print("  - Create comprehensive analysis (Advanced)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
