#!/usr/bin/env python3
"""
KAI Cookbook - Basic 06: Create Business Glossaries

This script demonstrates how to create and manage business glossaries in KAI.
Business glossaries define metric definitions and their SQL implementations.

API Endpoints:
- POST /api/v1/business_glossaries - Create a new business glossary entry
- GET /api/v1/business_glossaries - List glossaries (filtered by connection)
- GET /api/v1/business_glossaries/{id} - Get a specific glossary entry
- PUT /api/v1/business_glossaries/{id} - Update a glossary entry
- DELETE /api/v1/business_glossaries/{id} - Delete a glossary entry

Business Glossary Structure:
- metric: The business metric name
- alias: Alternative names for this metric
- sql: The SQL implementation of the metric
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


def list_business_glossaries(client: KAIAPIClient, connection_id: str) -> list:
    """List all business glossary entries for a connection."""
    print_subsection("Listing business glossaries")

    glossaries = client.get("/business_glossaries", params={"db_connection_id": connection_id})

    if not glossaries:
        print("  No business glossary entries found.")
        return []

    print(f"  Found {len(glossaries)} glossary entr(y/ies):")
    for gl in glossaries:
        print(f"    - ID: {gl['id']}")
        print(f"      Metric: {gl['metric']}")
        if gl.get('alias'):
            print(f"      Aliases: {', '.join(gl['alias'])}")
        print(f"      SQL: {gl['sql'][:60]}...")
        print()

    return glossaries


def create_business_glossary(
    client: KAIAPIClient,
    connection_id: str,
    metric: str,
    sql: str,
    alias: list[str] | None = None,
) -> dict:
    """Create a new business glossary entry."""
    print_subsection(f"Creating glossary entry: {metric}")

    payload = {
        "metric": metric,
        "sql": sql,
        "alias": alias or [],
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Metric: {metric}")
    if alias:
        print(f"  Aliases: {', '.join(alias)}")
    print(f"  SQL: {sql}")

    # db_connection_id is passed as query parameter
    glossary = client.post("/business_glossaries", json_data=payload, params={"db_connection_id": connection_id})
    print(f"  ✓ Glossary entry created: {glossary['id']}")

    return glossary


def get_business_glossary(client: KAIAPIClient, glossary_id: str) -> dict:
    """Get a specific business glossary entry."""
    print_subsection(f"Getting glossary entry: {glossary_id}")
    glossary = client.get(f"/business_glossaries/{glossary_id}")
    return glossary


def update_business_glossary(
    client: KAIAPIClient,
    glossary_id: str,
    metric: str | None = None,
    sql: str | None = None,
    alias: list[str] | None = None,
) -> dict:
    """Update a business glossary entry."""
    print_subsection(f"Updating glossary entry: {glossary_id}")

    payload = {}
    if metric is not None:
        payload["metric"] = metric
    if sql is not None:
        payload["sql"] = sql
    if alias is not None:
        payload["alias"] = alias

    updated = client.put(f"/business_glossaries/{glossary_id}", json_data=payload)
    print(f"  ✓ Glossary entry updated")

    return updated


def delete_business_glossary(client: KAIAPIClient, glossary_id: str) -> None:
    """Delete a business glossary entry."""
    print_subsection(f"Deleting glossary entry: {glossary_id}")
    result = client.delete(f"/business_glossaries/{glossary_id}")
    print(f"  ✓ Deleted: {result.get('message', 'Success')}")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 06: Business Glossaries")

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

    # Step 2: List existing glossaries
    print("\n[Step 2] List existing business glossaries")
    list_business_glossaries(client, connection_id)
    press_to_continue()

    # Step 3: Create example glossary entries
    print("\n[Step 3] Create example business glossary entries")

    # Example 1: Gross Revenue
    print("\n  Creating gross revenue metric...")
    press_to_continue()

    gl1 = create_business_glossary(
        client,
        connection_id,
        metric="Gross Revenue",
        sql="SELECT SUM(amount * quantity) FROM kro",
        alias=["total revenue", "sales", "income", "turnover"]
    )
    print_response(gl1, "Created Glossary 1")
    press_to_continue()

    # Example 2: Count Records
    print("\n  Creating count records metric...")
    press_to_continue()

    gl2 = create_business_glossary(
        client,
        connection_id,
        metric="Total Records",
        sql="SELECT COUNT(*) FROM proposal",
        alias=["count", "total", "row count"]
    )
    print_response(gl2, "Created Glossary 2")
    press_to_continue()

    # Example 3: Unique Values
    print("\n  Creating unique values metric...")
    press_to_continue()

    gl3 = create_business_glossary(
        client,
        connection_id,
        metric="Unique Items",
        sql="SELECT COUNT(DISTINCT id) FROM proposal",
        alias=["distinct", "unique count"]
    )
    print_response(gl3, "Created Glossary 3")
    press_to_continue()

    # Example 4: Monthly Recurring Revenue
    print("\n  Creating monthly recurring revenue metric...")
    press_to_continue()

    gl4 = create_business_glossary(
        client,
        connection_id,
        metric="Monthly Recurring Revenue",
        sql="SELECT SUM(amount) FROM kro WHERE status = 'active'",
        alias=["MRR", "recurring revenue"]
    )
    print_response(gl4, "Created Glossary 4")
    press_to_continue()

    # Step 4: List all glossaries
    print("\n[Step 4] List all business glossaries")
    all_glossaries = list_business_glossaries(client, connection_id)
    press_to_continue()

    # Step 5: Get specific glossary entry
    print("\n[Step 5] Get specific glossary entry details")
    if gl1:
        details = get_business_glossary(client, gl1["id"])
        print(f"  Metric: {details['metric']}")
        print(f"  Aliases: {details.get('alias', [])}")
        print(f"  SQL: {details['sql']}")
    press_to_continue()

    # Step 6: Update glossary entry
    print("\n[Step 6] Update a glossary entry")
    if gl1:
        print("  Updating gross revenue entry...")
        press_to_continue()

        updated = update_business_glossary(
            client,
            gl1["id"],
            alias=["total revenue", "sales", "income", "turnover", "gross sales"]
        )
        print_response(updated, "Updated Glossary Entry")
    press_to_continue()

    # Step 7: Cleanup
    print("\n[Step 7] Cleanup")
    print("  Created glossary entries can be deleted.")

    all_glossaries = list_business_glossaries(client, connection_id)
    if all_glossaries:
        if should_cleanup:
            print("  --cleanup enabled: Deleting created resources.")
            for gl in all_glossaries:
                if gl.get("metadata", {}).get("created_by") == "cookbook":
                    delete_business_glossary(client, gl["id"])
        else:
            print("  --no-cleanup: Preserving created resources.")
            print("  Run with --cleanup flag to remove created resources.")

    print_section("Demo Complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
