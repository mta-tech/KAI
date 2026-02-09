#!/usr/bin/env python3
"""
KAI Cookbook - Basic 02: List Table Descriptions

This script demonstrates how to list and view table descriptions in KAI.

API Endpoints:
- GET /api/v1/table-descriptions - List table descriptions (with optional filtering)
- GET /api/v1/table-descriptions/{id} - Get a specific table description
- DELETE /api/v1/table-descriptions/{id} - Delete a table description
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    KAIAPIClient,
    SAMPLE_DB_ALIAS,
    parse_cookbook_args,
    print_section,
    print_subsection,
    print_response,
    press_to_continue,
    find_by_name,
)


def get_connection_id_by_alias(client: KAIAPIClient, alias: str) -> str | None:
    """Get connection ID by alias."""
    connections = client.get("/database-connections")
    for conn in connections:
        if conn.get("alias") == alias:
            return conn.get("id")
    return None


def list_table_descriptions(
    client: KAIAPIClient,
    db_connection_id: str,
    table_name: str | None = None,
) -> list[dict]:
    """List all table descriptions for a connection."""
    print_subsection("Listing table descriptions")

    params = {"db_connection_id": db_connection_id}
    if table_name:
        params["table_name"] = table_name

    descriptions = client.get("/table-descriptions", params=params)

    if not descriptions:
        print("  No table descriptions found.")
        print("  Tip: Run schema sync first (Basic 03) to create table descriptions.")
        return []

    print(f"  Found {len(descriptions)} table description(s):")
    for desc in descriptions:
        print(f"    - ID: {desc['id']}")
        print(f"      Table: {desc['table_name']}")
        print(f"      Schema: {desc.get('db_schema', 'N/A')}")
        if desc.get('table_description'):
            print(f"      Description: {desc['table_description'][:60]}...")
        print(f"      Columns: {len(desc.get('columns', []))}")
        print()

    return descriptions


def get_table_description(client: KAIAPIClient, table_description_id: str) -> dict:
    """Get detailed information about a specific table."""
    print_subsection(f"Getting table description details: {table_description_id}")

    description = client.get(f"/table-descriptions/{table_description_id}")

    print(f"  Table: {description['table_name']}")
    print(f"  Schema: {description['schema_name']}")
    if description.get('table_description'):
        print(f"  Description: {description['table_description']}")
    print(f"  Columns ({len(description.get('columns', []))}):")

    for col in description.get('columns', []):
        print(f"    - {col['name']} ({col['data_type']})")
        if col.get('description'):
            print(f"      {col['description']}")
        if col.get('is_primary_key'):
            print(f"      [PRIMARY KEY]")
        if col.get('foreign_key'):
            fk = col['foreign_key']
            print(f"      → REFERENCES {fk['reference_table']}({fk['field_name']})")

    return description


def delete_table_description(client: KAIAPIClient, table_description_id: str) -> None:
    """Delete a table description."""
    print_subsection(f"Deleting table description: {table_description_id}")
    result = client.delete(f"/table-descriptions/{table_description_id}")
    print(f"  ✓ Deleted: {result.get('message', 'Success')}")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 02: Table Descriptions")

    client = KAIAPIClient()

    # Use sample database from environment
    print(f"\nUsing sample database: {SAMPLE_DB_ALIAS}")
    print("  (from SAMPLE_DB_URI in .env)")
    print("\nMake sure to run '01_create_database_connection.py' first!")

    press_to_continue("Press Enter to continue or Ctrl+C to cancel...")

    # Step 1: Get the connection ID
    print("\n[Step 1] Get connection ID")
    connection_id = get_connection_id_by_alias(client, SAMPLE_DB_ALIAS)

    if not connection_id:
        print(f"  ✗ Connection '{SAMPLE_DB_ALIAS}' not found!")
        print(f"  Please run '01_create_database_connection.py' first.")
        return

    print(f"  ✓ Found connection: {SAMPLE_DB_ALIAS} (ID: {connection_id})")
    press_to_continue()

    # Step 2: List all table descriptions
    print("\n[Step 2] List all table descriptions")
    descriptions = list_table_descriptions(client, connection_id)
    press_to_continue()

    # Step 3: If no descriptions, guide user
    if not descriptions:
        print("\n[Step 3] No table descriptions found")
        print("  Table descriptions are created when you sync schemas.")
        print("  Run '03_sync_schemas.py' to create table descriptions.")
        print_section("Demo Complete")
        return

    # Step 4: Get details of the first table
    print("\n[Step 4] Get detailed table description")
    first_table = descriptions[0]
    table_id = first_table["id"]
    get_table_description(client, table_id)
    press_to_continue()

    # Step 5: Filter by table name
    print("\n[Step 5] Filter by specific table name")
    first_table_name = first_table["table_name"]
    print(f"  Searching for table: {first_table_name}")
    filtered = list_table_descriptions(client, connection_id, first_table_name)
    press_to_continue()

    # Step 6: Demo update table description
    print("\n[Step 6] Update table description")
    print("  Note: You can add AI-generated descriptions to tables.")
    print("  This is typically done during schema sync with AI enabled.")
    press_to_continue()

    # Step 7: Cleanup option
    print("\n[Step 7] Cleanup")
    print(f"  Table descriptions can be deleted individually if needed.")
    if should_cleanup:
        print("  --cleanup enabled: Delete would happen here.")
        print("  (Skipping actual delete for safety)")
    else:
        print("  --no-cleanup: Preserving table descriptions.")
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
