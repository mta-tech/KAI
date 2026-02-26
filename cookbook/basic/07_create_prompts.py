#!/usr/bin/env python3
"""
KAI Cookbook - Basic 07: Create Prompts

This script demonstrates how to create and manage prompts in KAI.
Prompts are natural language queries that can be converted to SQL.

API Endpoints:
- POST /api/v1/prompts - Create a new prompt
- GET /api/v1/prompts - List prompts (filtered by connection)
- GET /api/v1/prompts/{id} - Get a specific prompt
- PUT /api/v1/prompts/{id} - Update a prompt's metadata

Prompts Structure:
- text: The natural language query text
- db_connection_id: The database connection to use
- schemas: Optional list of schemas to query
- context: Optional context information for the prompt
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


def list_prompts(client: KAIAPIClient, connection_id: str) -> list:
    """List all prompts for a connection."""
    print_subsection("Listing prompts")

    prompts = client.get("/prompts", params={"db_connection_id": connection_id})

    if not prompts:
        print("  No prompts found.")
        return []

    print(f"  Found {len(prompts)} prompt(s):")
    for pr in prompts[:5]:
        print(f"    - ID: {pr['id']}")
        print(f"      Text: {pr['text'][:60]}...")
        print(f"      Schemas: {pr.get('schemas', [])}")
        print()

    if len(prompts) > 5:
        print(f"  ... and {len(prompts) - 5} more")

    return prompts


def create_prompt(
    client: KAIAPIClient,
    connection_id: str,
    text: str,
    schemas: list[str] | None = None,
    context: list[dict] | None = None,
) -> dict:
    """Create a new prompt."""
    print_subsection("Creating prompt")

    payload = {
        "text": text,
        "db_connection_id": connection_id,
        "schemas": schemas,
        "context": context,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Text: {text}")
    if schemas:
        print(f"  Schemas: {schemas}")

    prompt = client.post("/prompts", json_data=payload)
    print(f"  ✓ Prompt created: {prompt['id']}")

    return prompt


def get_prompt(client: KAIAPIClient, prompt_id: str) -> dict:
    """Get a specific prompt."""
    print_subsection(f"Getting prompt: {prompt_id}")
    prompt = client.get(f"/prompts/{prompt_id}")
    return prompt


def update_prompt_metadata(
    client: KAIAPIClient,
    prompt_id: str,
    metadata: dict,
) -> dict:
    """Update a prompt's metadata."""
    print_subsection(f"Updating prompt metadata: {prompt_id}")

    payload = {"metadata": metadata}
    updated = client.put(f"/prompts/{prompt_id}", json_data=payload)
    print(f"  ✓ Prompt metadata updated")

    return updated


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 07: Prompts")

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

    # Step 2: List existing prompts
    print("\n[Step 2] List existing prompts")
    list_prompts(client, connection_id)
    press_to_continue()

    # Step 3: Create example prompts
    print("\n[Step 3] Create example prompts")

    # Example 1: Sales query
    print("\n  Creating sales query prompt...")
    press_to_continue()

    pr1 = create_prompt(
        client,
        connection_id,
        "What is the total revenue for each month in the current year?",
        schemas=["public"]
    )
    print_response(pr1, "Created Prompt 1")
    press_to_continue()

    # Example 2: Customer query
    print("\n  Creating customer query prompt...")
    press_to_continue()

    pr2 = create_prompt(
        client,
        connection_id,
        "Who are our top 10 customers by spending?",
        schemas=["public"]
    )
    print_response(pr2, "Created Prompt 2")
    press_to_continue()

    # Example 3: Product query with context
    print("\n  Creating product query prompt with context...")
    press_to_continue()

    pr3 = create_prompt(
        client,
        connection_id,
        "What products are selling best?",
        schemas=["public"],
        context=[
            {"key": "time_range", "value": "last 30 days"},
            {"key": "metric", "value": "quantity sold"}
        ]
    )
    print_response(pr3, "Created Prompt 3 (with context)")
    press_to_continue()

    # Example 4: Complex analytics query
    print("\n  Creating analytics query prompt...")
    press_to_continue()

    pr4 = create_prompt(
        client,
        connection_id,
        "Show me the trend of new customer signups over the past 6 months",
        schemas=["public"]
    )
    print_response(pr4, "Created Prompt 4")
    press_to_continue()

    # Step 4: List all prompts
    print("\n[Step 4] List all prompts")
    all_prompts = list_prompts(client, connection_id)
    press_to_continue()

    # Step 5: Get specific prompt
    print("\n[Step 5] Get specific prompt details")
    if pr1:
        details = get_prompt(client, pr1["id"])
        print(f"  Text: {details['text']}")
        print(f"  Connection ID: {details['db_connection_id']}")
        print(f"  Schemas: {details.get('schemas', [])}")
        print(f"  Context: {details.get('context', [])}")
    press_to_continue()

    # Step 6: Update prompt metadata
    print("\n[Step 6] Update prompt metadata")
    if pr1:
        print("  Adding metadata to prompt...")
        press_to_continue()

        current = get_prompt(client, pr1["id"])
        metadata = current.get("metadata", {})
        metadata["category"] = "analytics"
        metadata["priority"] = "high"

        updated = update_prompt_metadata(client, pr1["id"], metadata)
        print_response(updated, "Updated Prompt Metadata")
    press_to_continue()

    # Step 7: Cleanup
    print("\n[Step 7] Cleanup")
    print("  Prompts are typically kept for reference and SQL generation.")
    print("  They can be deleted if needed, but are usually archived.")

    if should_cleanup:
        print("  --cleanup enabled: Prompts will be preserved.")
        print("  (Prompts are not typically deleted as they are reference material)")
    else:
        print("  --no-cleanup: Preserving created resources.")

    print_section("Demo Complete")
    print("\nNext Steps:")
    print("  - Use these prompts for SQL generation (see Basic 08)")
    print("  - Combine prompts with context stores for better results")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
