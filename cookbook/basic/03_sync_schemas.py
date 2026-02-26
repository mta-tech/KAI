#!/usr/bin/env python3
"""
KAI Cookbook - Basic 03: Sync Database Schemas

This script demonstrates how to sync database schemas with KAI.
Schema sync creates table descriptions by scanning the database structure.

API Endpoints:
- POST /api/v1/table-descriptions/sync-schemas - Sync schemas (scan database)
- POST /api/v1/table-descriptions/refresh - Refresh table descriptions
- PUT /api/v1/table-descriptions/{id} - Update a table description

Background Task:
Schema sync is a background task. You can monitor progress and get results
once the task completes.
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
    find_by_name,
    parse_cookbook_args,
)


def get_connection_id_by_alias(client: KAIAPIClient, alias: str) -> str | None:
    """Get connection ID by alias."""
    connections = client.get("/database-connections")
    for conn in connections:
        if conn.get("alias") == alias:
            return conn.get("id")
    return None


def refresh_table_descriptions(
    client: KAIAPIClient,
    connection_id: str,
) -> list:
    """
    Refresh all table descriptions for a connection.

    This scans the database and creates table descriptions (table names only).
    The API expects database_connection_id as a query parameter.
    """
    print_subsection("Refreshing table descriptions")

    print("  Scanning database for tables... (this may take a moment)")
    # The API expects database_connection_id as a query parameter, not in request body
    descriptions = client.post("/table-descriptions/refresh", params={"database_connection_id": connection_id})

    print(f"  ✓ Refresh complete! Found {len(descriptions)} table(s)")

    for desc in descriptions:
        print(f"    - {desc.get('db_schema', 'N/A')}.{desc['table_name']}")
        print(f"      Columns: {len(desc.get('columns', []))}")

    return descriptions


def sync_schemas(
    client: KAIAPIClient,
    table_description_ids: list[str],
    enable_ai: bool = True,
) -> list:
    """
    Sync schema details for existing table descriptions.

    This scans columns for existing tables and optionally generates AI descriptions.
    Note: Requires existing table descriptions (run refresh first).
    """
    print_subsection("Syncing schema details")

    payload = {
        "table_description_ids": table_description_ids,
    }

    if enable_ai:
        print("  AI-enabled sync: Will generate table and column descriptions")
        print("  Note: This requires LLM API keys configured in the server")
        payload["instruction"] = "Generate clear descriptions for all tables and columns"
        payload["llm_config"] = {
            "provider": "google",
            "model": "gemini-2.0-flash-exp"
        }
    else:
        print("  Basic sync: Will scan columns without AI descriptions")

    print(f"  Scanning {len(table_description_ids)} table(s)...")
    descriptions = client.post("/table-descriptions/sync-schemas", json_data=payload)

    print(f"  ✓ Sync complete! Updated {len(descriptions)} table description(s)")

    for desc in descriptions:
        print(f"    - {desc['db_schema']}.{desc['table_name']}")
        print(f"      Columns: {len(desc.get('columns', []))}")

    return descriptions


def update_table_description(
    client: KAIAPIClient,
    table_description_id: str,
    table_description: str | None = None,
    column_updates: list[dict] | None = None,
) -> dict:
    """Update a table description."""
    print_subsection(f"Updating table description: {table_description_id}")

    payload = {"metadata": {}}

    if table_description:
        payload["table_description"] = table_description
        print(f"  Updating table description")

    if column_updates:
        payload["columns"] = column_updates
        print(f"  Updating {len(column_updates)} column(s)")

    updated = client.put(f"/table-descriptions/{table_description_id}", json_data=payload)
    print(f"  ✓ Updated successfully")

    return updated


def wait_for_sync(client: KAIAPIClient, connection_id: str, timeout: int = 60) -> bool:
    """Wait for sync to complete by polling for table descriptions."""
    print("  Waiting for sync to complete...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            descriptions = client.get("/table-descriptions", params={"db_connection_id": connection_id})
            if descriptions and len(descriptions) > 0:
                return True
        except Exception:
            pass
        time.sleep(2)

    return False


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 03: Sync Database Schemas")

    client = KAIAPIClient()

    # Use sample database from environment
    example_alias = SAMPLE_DB_ALIAS
    print(f"\nUsing connection alias: {example_alias}")
    print("(Edit the script to change this value)")

    press_to_continue("Press Enter to continue or Ctrl+C to cancel...")

    # Step 1: Get the connection ID
    print("\n[Step 1] Get connection ID")
    connection_id = get_connection_id_by_alias(client, example_alias)

    if not connection_id:
        print(f"  ✗ Connection '{example_alias}' not found!")
        print(f"  Please run '01_create_database_connection.py' first.")
        return

    print(f"  ✓ Found connection: {example_alias} (ID: {connection_id})")
    press_to_continue()

    # Step 2: Check existing table descriptions
    print("\n[Step 2] Check existing table descriptions")
    existing = client.get("/table-descriptions", params={"db_connection_id": connection_id})

    if existing:
        print(f"  Found {len(existing)} existing table description(s):")
        for desc in existing[:5]:
            print(f"    - {desc.get('db_schema', 'N/A')}.{desc['table_name']}")
        if len(existing) > 5:
            print(f"    ... and {len(existing) - 5} more")

        if should_cleanup:
            choice = input("\n  Resync all tables? (y/N): ").strip().lower()
            if choice != "y":
                print("  Skipping sync.")
                press_to_continue()
        else:
            print("  --no-cleanup: Skipping resync prompt.")
    else:
        print("  No existing table descriptions found.")
    press_to_continue()

    # Step 3: Refresh table descriptions (creates table entries)
    print("\n[Step 3] Refresh table descriptions")
    print("  This scans the database and creates table entries.")
    press_to_continue("Press Enter to refresh...")

    try:
        descriptions = refresh_table_descriptions(client, connection_id)
    except Exception as e:
        print(f"  ✗ Refresh failed: {e}")
        print(f"  Make sure:")
        print(f"    - The database is running")
        print(f"    - The connection credentials are correct")
        return
    press_to_continue()

    # Step 4: Sync schema details (scan columns)
    print("\n[Step 4] Scan table columns")
    print("  Choose sync mode:")
    print("    1. Basic scan (columns only)")
    print("    2. AI-enabled scan (with descriptions)")

    mode = input("  Enter choice (1 or 2, default: 2): ").strip() or "2"
    enable_ai = mode == "2"

    press_to_continue("Press Enter to scan columns...")

    # Get all table description IDs
    table_descriptions = client.get("/table-descriptions", params={"db_connection_id": connection_id})
    table_ids = [t["id"] for t in table_descriptions]

    try:
        descriptions = sync_schemas(client, table_ids, enable_ai=enable_ai)
        print_response(descriptions[:2], "Sample Updated Descriptions")
    except Exception as e:
        print(f"  ✗ Scan failed: {e}")
        print(f"  Make sure:")
        print(f"    - LLM API keys are configured (for AI mode)")
        return
    press_to_continue()

    # Step 5: View synced tables
    print("\n[Step 5] View synced tables")
    all_descriptions = client.get("/table-descriptions", params={"db_connection_id": connection_id})
    print(f"  Total table descriptions: {len(all_descriptions)}")

    for desc in all_descriptions[:5]:
        print(f"    - {desc.get('db_schema', 'N/A')}.{desc['table_name']}")
        if desc.get('table_description'):
            print(f"      {desc['table_description'][:60]}...")
    press_to_continue()

    # Step 6: Demo update a table description
    print("\n[Step 6] Update a table description")
    if all_descriptions:
        first_table = all_descriptions[0]
        table_id = first_table["id"]

        print(f"  Updating: {first_table['table_name']}")
        press_to_continue("Press Enter to update...")

        try:
            updated = update_table_description(
                client,
                table_id,
                table_description=f"Updated description for {first_table['table_name']}"
            )
            print(f"  ✓ Updated: {updated['table_description']}")
        except Exception as e:
            print(f"  ! Update skipped: {e}")
    press_to_continue()

    # Step 7: Summary
    print("\n[Step 7] Summary")
    print("  Schema sync process:")
    print("    1. Refresh - Creates table entries by scanning database")
    print("    2. Sync schemas - Scans columns and optionally generates AI descriptions")
    print("\n  Use cases:")
    print("    - Initial database setup")
    print("    - After schema changes")
    print("    - Adding AI descriptions for better natural language queries")

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
