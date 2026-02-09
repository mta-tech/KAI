#!/usr/bin/env python3
"""
KAI Cookbook - Advanced 02: Comprehensive Analysis

This script demonstrates comprehensive analysis that combines:
1. Prompt → SQL Generation
2. SQL Execution
3. Statistical Analysis
4. Natural Language Insights
5. Chart Recommendations

This is the most powerful end-to-end feature in KAI.

API Endpoints:
- POST /api/v1/analysis/comprehensive - End-to-end analysis in one call
- POST /api/v1/sql-generations/{id}/analysis - Analyze existing SQL generation
- GET /api/v1/analysis/{id} - Get analysis results

Comprehensive Analysis Features:
- Automatic SQL generation from natural language
- Data execution and retrieval
- Statistical analysis (trends, patterns, anomalies)
- Natural language insights generation
- Chart type recommendations
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


def create_comprehensive_analysis(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    max_rows: int = 100,
    use_deep_agent: bool = False,
) -> dict:
    """Create a comprehensive end-to-end analysis."""
    print_subsection("Creating comprehensive analysis")

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
        "max_rows": max_rows,
        "use_deep_agent": use_deep_agent,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Query: {text}")
    print(f"  Max rows: {max_rows}")
    print(f"  Deep Agent: {use_deep_agent}")
    print("  Running end-to-end analysis...")
    print("  (This may take a while...)")

    analysis = client.post("/analysis/comprehensive", json_data=payload)

    print(f"  ✓ Analysis complete!")
    print(f"  Prompt ID: {analysis['prompt_id']}")
    print(f"  SQL Generation ID: {analysis['sql_generation_id']}")
    print(f"  Analysis ID: {analysis.get('analysis_id', 'N/A')}")
    print(f"  Status: {analysis['sql_status']}")

    return analysis


def create_analysis_from_sql(
    client: KAIAPIClient,
    sql_gen_id: str,
    llm_provider: str = "google",
    llm_model: str = "gemini-2.0-flash-exp",
    max_rows: int = 100,
) -> dict:
    """Create analysis from an existing SQL generation."""
    print_subsection("Creating analysis from SQL generation")

    payload = {
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        },
        "max_rows": max_rows,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  SQL Generation ID: {sql_gen_id}")
    print("  Analyzing results...")

    analysis = client.post(f"/sql-generations/{sql_gen_id}/analysis", json_data=payload)

    print(f"  ✓ Analysis complete!")

    return analysis


def get_analysis(client: KAIAPIClient, analysis_id: str) -> dict:
    """Get a specific analysis."""
    print_subsection(f"Getting analysis: {analysis_id}")
    analysis = client.get(f"/analysis/{analysis_id}")
    return analysis


def print_analysis_results(analysis: dict) -> None:
    """Pretty print analysis results."""
    print("\n  Analysis Summary:")
    print(f"    {analysis.get('summary', 'N/A')}")

    if analysis.get('insights'):
        print(f"\n  Key Insights ({len(analysis['insights'])}):")
        for i, insight in enumerate(analysis['insights'][:3], 1):
            print(f"    {i}. {insight.get('title', 'Untitled')}")
            print(f"       {insight.get('description', 'N/A')[:100]}...")
            if insight.get('significance'):
                print(f"       Significance: {insight['significance']}")

    if analysis.get('chart_recommendations'):
        print(f"\n  Chart Recommendations ({len(analysis['chart_recommendations'])}):")
        for i, chart in enumerate(analysis['chart_recommendations'][:3], 1):
            print(f"    {i}. {chart.get('chart_type', 'Unknown')}: {chart.get('title', 'Untitled')}")
            print(f"       {chart.get('description', 'N/A')[:80]}...")

    print(f"\n  Data Stats:")
    print(f"    Rows: {analysis.get('row_count', 0)}")
    print(f"    Columns: {analysis.get('column_count', 0)}")

    if analysis.get('input_tokens_used'):
        print(f"  Tokens:")
        print(f"    Input: {analysis['input_tokens_used']}")
        print(f"    Output: {analysis['output_tokens_used']}")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Advanced 02: Comprehensive Analysis")

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

    # Step 2: Run comprehensive analysis
    print("\n[Step 2] Run comprehensive analysis")
    print("  This will: generate SQL, execute it, and analyze results")
    press_to_continue("Press Enter to run analysis...")

    try:
        analysis = create_comprehensive_analysis(
            client,
            connection_id,
            "Analyze monthly revenue trends and identify any patterns",
            llm_provider="google",
            llm_model="gemini-2.0-flash-exp",
            max_rows=100
        )

        print_response(analysis, "Analysis Results (Overview)")
    except Exception as e:
        print(f"  ! Analysis failed: {e}")
        print("  Make sure:")
        print("    - LLM API keys are configured")
        print("    - Database has relevant tables (orders, sales, etc.)")
        print("    - Database is running and accessible")
        return
    press_to_continue()

    # Step 3: Get detailed analysis
    print("\n[Step 3] Get detailed analysis")
    if analysis.get('analysis_id'):
        try:
            details = get_analysis(client, analysis['analysis_id'])
            print_analysis_results(details)
        except Exception as e:
            print(f"  ! Could not fetch details: {e}")
    else:
        # Show info from the response itself
        print_analysis_results(analysis)
    press_to_continue()

    # Step 4: Another analysis example
    print("\n[Step 4] Run another analysis")
    press_to_continue("Press Enter to run...")

    try:
        analysis2 = create_comprehensive_analysis(
            client,
            connection_id,
            "What are the top performing products and why?",
            llm_provider="google",
            llm_model="gemini-2.0-flash-exp",
            max_rows=50
        )

        print_analysis_results(analysis2)
    except Exception as e:
        print(f"  ! Analysis failed: {e}")
    press_to_continue()

    # Step 5: Show execution time
    print("\n[Step 5] Execution summary")
    if analysis.get('execution_time'):
        print("  Execution times:")
        for step, time_val in analysis['execution_time'].items():
            print(f"    {step}: {time_val}")

    if analysis.get('input_tokens_used'):
        print(f"\n  Token Usage:")
        print(f"    Input: {analysis['input_tokens_used']}")
        print(f"    Output: {analysis['output_tokens_used']}")
    press_to_continue()

    # Step 6: Summary
    print("\n[Step 6] Summary")
    print("  Comprehensive Analysis combines:")
    print("    1. Natural language → SQL generation")
    print("    2. SQL execution")
    print("    3. Statistical analysis")
    print("    4. Insight generation")
    print("    5. Chart recommendations")
    print("\n  Use cases:")
    print("    - Business intelligence dashboards")
    print("    - Automated reporting")
    print("    - Data exploration")
    print("    - Executive summaries")

    if should_cleanup:
        print("  --cleanup enabled: Analysis results will be preserved.")
        print("  (Analysis results are not typically deleted as they are reference material)")
    else:
        print("  --no-cleanup: Preserving created resources.")

    print_section("Demo Complete")
    print("\nNext Steps:")
    print("  - Integrate into your application")
    print("  - Create scheduled reports")
    print("  - Build interactive dashboards")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
