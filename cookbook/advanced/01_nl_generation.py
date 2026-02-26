#!/usr/bin/env python3
"""
KAI Cookbook - Advanced 01: Natural Language Generation

This script demonstrates how to generate natural language insights from SQL results.
After executing SQL, KAI can analyze the results and generate human-readable insights.

API Endpoints:
- POST /api/v1/sql-generations/{id}/nl-generations - Generate NL insights from SQL results
- POST /api/v1/prompts/{id}/sql-generations/nl-generations - Create SQL + NL generation
- POST /api/v1/prompts/sql-generations/nl-generations - One-call: prompt + SQL + NL
- GET /api/v1/nl-generations - List NL generations (filtered by SQL generation)
- GET /api/v1/nl-generations/{id} - Get a specific NL generation
- PUT /api/v1/nl-generations/{id} - Update NL generation metadata

NL Generation Structure:
- Takes SQL execution results as input
- Generates natural language summary and insights
- Uses LLM to analyze patterns and trends
"""

import sys
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


def create_sql_generation_for_nl(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
) -> dict | None:
    """Create a SQL generation for NL analysis."""
    print_subsection("Creating SQL generation")

    # First create prompt
    prompt = client.post("/prompts", json_data={
        "text": text,
        "db_connection_id": connection_id,
        "metadata": {"created_by": "cookbook"}
    })

    # Then generate SQL
    try:
        sql_gen = client.post(f"/prompts/{prompt['id']}/sql-generations", json_data={
            "llm_config": {"provider": "google", "model": "gemini-2.0-flash-exp"},
            "metadata": {"created_by": "cookbook"}
        })
        return sql_gen
    except Exception as e:
        print(f"  ! SQL generation failed: {e}")
        return None


def create_nl_generation(
    client: KAIAPIClient,
    sql_gen_id: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    max_rows: int = 100,
) -> dict:
    """Generate natural language insights from SQL results."""
    print_subsection("Generating natural language insights")

    payload = {
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        },
        "max_rows": max_rows,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  SQL Generation ID: {sql_gen_id}")
    print(f"  Max rows: {max_rows}")
    print("  Analyzing results and generating insights...")

    nl_gen = client.post(f"/sql-generations/{sql_gen_id}/nl-generations", json_data=payload)

    print(f"  ✓ NL Generation created: {nl_gen['id']}")
    print(f"  Text: {nl_gen.get('text', 'N/A')[:200]}...")

    return nl_gen


def create_sql_and_nl(
    client: KAIAPIClient,
    prompt_id: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    max_rows: int = 100,
) -> dict:
    """Create SQL generation and NL insights in one call."""
    print_subsection("Creating SQL and NL generation")

    payload = {
        "sql_generation": {
            "llm_config": {"provider": llm_provider, "model": llm_model},
            "metadata": {"created_by": "cookbook"}
        },
        "llm_config": {"provider": llm_provider, "model": llm_model},
        "max_rows": max_rows,
        "metadata": {"created_by": "cookbook"}
    }

    print("  Generating SQL and analyzing results...")

    nl_gen = client.post(f"/prompts/{prompt_id}/sql-generations/nl-generations", json_data=payload)

    print(f"  ✓ Complete!")
    print(f"  NL Generation ID: {nl_gen['id']}")
    print(f"  Insights: {nl_gen.get('text', 'N/A')[:200]}...")

    return nl_gen


def create_prompt_sql_nl(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    max_rows: int = 100,
) -> dict:
    """One-call: prompt, SQL generation, and NL insights."""
    print_subsection("End-to-end: Prompt → SQL → Insights")

    payload = {
        "sql_generation": {
            "prompt": {
                "text": text,
                "db_connection_id": connection_id,
                "schemas": ["public"],
                "metadata": {"created_by": "cookbook"}
            },
            "llm_config": {"provider": llm_provider, "model": llm_model},
            "metadata": {"created_by": "cookbook"}
        },
        "llm_config": {"provider": llm_provider, "model": llm_model},
        "max_rows": max_rows,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Prompt: {text}")
    print("  Generating SQL and insights...")

    nl_gen = client.post("/prompts/sql-generations/nl-generations", json_data=payload)

    print(f"  ✓ Complete!")
    print(f"  Insights: {nl_gen.get('text', 'N/A')[:200]}...")

    return nl_gen


def get_nl_generation(client: KAIAPIClient, nl_gen_id: str) -> dict:
    """Get a specific NL generation."""
    print_subsection(f"Getting NL generation: {nl_gen_id}")
    nl_gen = client.get(f"/nl-generations/{nl_gen_id}")
    return nl_gen


def list_nl_generations(client: KAIAPIClient, sql_gen_id: str) -> list:
    """List NL generations for a SQL generation."""
    print_subsection("Listing NL generations")
    nl_gens = client.get("/nl-generations", params={"sql_generation_id": sql_gen_id})
    return nl_gens


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Advanced 01: Natural Language Generation")

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

    # Step 2: Create SQL generation for NL analysis
    print("\n[Step 2] Create SQL generation for NL analysis")
    print("  First, we need a SQL generation to analyze")
    press_to_continue()

    sql_gen = create_sql_generation_for_nl(
        client,
        connection_id,
        "What is the total revenue by month?"
    )

    if not sql_gen:
        print("  ! Skipping NL generation - SQL generation failed")
        print("  Make sure:")
        print("    - LLM API keys are configured")
        print("    - Database has relevant tables")
        return
    press_to_continue()

    # Step 3: Generate NL insights from SQL
    print("\n[Step 3] Generate natural language insights")
    press_to_continue("Press Enter to generate insights...")

    try:
        nl_gen = create_nl_generation(client, sql_gen["id"])
        print_response(nl_gen, "Generated Insights")
    except Exception as e:
        print(f"  ! NL generation failed: {e}")
        print("  This might be due to:")
        print("    - SQL execution failed")
        print("    - No results returned")
        print("    - LLM API not configured")
        return
    press_to_continue()

    # Step 4: Get NL generation details
    print("\n[Step 4] Get NL generation details")
    if nl_gen:
        details = get_nl_generation(client, nl_gen["id"])
        print(f"  Full Text:\n    {details.get('text', 'N/A')}")
    press_to_continue()

    # Step 5: One-call: prompt + SQL + NL
    print("\n[Step 5] One-call: Prompt → SQL → Insights")
    print("  This combines everything into a single API call")
    press_to_continue("Press Enter to run...")

    try:
        nl_gen2 = create_prompt_sql_nl(
            client,
            connection_id,
            "Show me the top 5 products by sales volume"
        )
        print_response(nl_gen2, "End-to-End Results")
    except Exception as e:
        print(f"  ! End-to-end generation failed: {e}")
    press_to_continue()

    # Step 6: List NL generations
    print("\n[Step 6] List NL generations for a SQL generation")
    if sql_gen:
        nl_gens = list_nl_generations(client, sql_gen["id"])
        print(f"  Found {len(nl_gens)} NL generation(s)")
        for nl in nl_gens:
            print(f"    - ID: {nl['id']}")
            print(f"      Text preview: {nl.get('text', 'N/A')[:80]}...")
    press_to_continue()

    # Step 7: Summary
    print("\n[Step 7] Summary")
    print("  Natural Language Generation converts SQL results into insights.")
    print("  Use cases:")
    print("    - Automated reporting")
    print("    - Business intelligence summaries")
    print("    - Executive dashboards")
    print("    - Data storytelling")

    if should_cleanup:
        print("  --cleanup enabled: NL generations will be preserved.")
        print("  (NL generations are not typically deleted as they are reference material)")
    else:
        print("  --no-cleanup: Preserving created resources.")

    print_section("Demo Complete")
    print("\nNext Steps:")
    print("  - Create comprehensive analysis (Advanced 02)")
    print("  - Use RAG for document-based insights (Advanced 03)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
