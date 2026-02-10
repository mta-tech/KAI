#!/usr/bin/env python3
"""
KAI Cookbook - Basic 09: Aliases

This script demonstrates how to create and manage aliases in KAI.
Aliases are alternative names for tables, columns, or other database objects.
They help map business terminology to technical schema names.

API Endpoints:
- POST /api/v1/aliases - Create a new alias
- GET /api/v1/aliases - List aliases (filtered by connection and optional target type)
- GET /api/v1/aliases/{id} - Get a specific alias
- GET /api/v1/aliases/get-by-name - Find an alias by name
- PUT /api/v1/aliases/{id} - Update an alias
- DELETE /api/v1/aliases/{id} - Delete an alias

Alias Structure:
- name: The alias/alternative name
- target_name: The actual table/column name in the database
- target_type: Type of target (table, column)
- description: What this alias represents
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


def list_aliases(
    client: KAIAPIClient,
    connection_id: str,
    target_type: str | None = None,
) -> list:
    """List all aliases for a connection."""
    print_subsection("Listing aliases")

    params = {"db_connection_id": connection_id}
    if target_type:
        params["target_type"] = target_type

    aliases = client.get("/aliases", params=params)

    if not aliases:
        print("  No aliases found.")
        return []

    type_filter = f" (type: {target_type})" if target_type else ""
    print(f"  Found {len(aliases)} alias(es){type_filter}:")

    for al in aliases:
        print(f"    - ID: {al['id']}")
        print(f"      Name: {al['name']}")
        print(f"      Target: {al['target_type']}.{al['target_name']}")
        if al.get('description'):
            print(f"      Description: {al['description']}")
        print()

    return aliases


def create_alias(
    client: KAIAPIClient,
    connection_id: str,
    name: str,
    target_name: str,
    target_type: str,
    description: str | None = None,
) -> dict:
    """Create a new alias."""
    print_subsection(f"Creating alias: {name}")

    payload = {
        "db_connection_id": connection_id,
        "name": name,
        "target_name": target_name,
        "target_type": target_type,
        "description": description,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Alias: {name} → {target_type}.{target_name}")
    if description:
        print(f"  Description: {description}")

    alias = client.post("/aliases", json_data=payload)
    print(f"  ✓ Alias created: {alias['id']}")

    return alias


def get_alias_by_name(
    client: KAIAPIClient,
    name: str,
    connection_id: str,
) -> dict | None:
    """Find an alias by name."""
    print_subsection(f"Finding alias: {name}")

    params = {"name": name, "db_connection_id": connection_id}
    try:
        alias = client.get("/aliases/get-by-name", params=params)
        print(f"  ✓ Found: {alias['name']} → {alias['target_name']}")
        return alias
    except Exception:
        print(f"  ! Alias not found: {name}")
        return None


def get_alias(client: KAIAPIClient, alias_id: str) -> dict:
    """Get a specific alias."""
    print_subsection(f"Getting alias: {alias_id}")
    alias = client.get(f"/aliases/{alias_id}")
    return alias


def update_alias(
    client: KAIAPIClient,
    alias_id: str,
    name: str | None = None,
    target_name: str | None = None,
    description: str | None = None,
) -> dict:
    """Update an alias."""
    print_subsection(f"Updating alias: {alias_id}")

    payload = {}
    if name is not None:
        payload["name"] = name
    if target_name is not None:
        payload["target_name"] = target_name
    if description is not None:
        payload["description"] = description

    updated = client.put(f"/aliases/{alias_id}", json_data=payload)
    print(f"  ✓ Alias updated")

    return updated


def delete_alias(client: KAIAPIClient, alias_id: str) -> None:
    """Delete an alias."""
    print_subsection(f"Deleting alias: {alias_id}")
    result = client.delete(f"/aliases/{alias_id}")
    print(f"  ✓ Deleted")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 09: Aliases")

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

    # Step 2: List existing aliases
    print("\n[Step 2] List existing aliases")
    list_aliases(client, connection_id)
    press_to_continue()

    # Step 3: Create example aliases for tables
    print("\n[Step 3] Create table aliases")
    print("  Mapping business terms to actual table names")

    # Example: orders table
    print("\n  Creating alias for orders table...")
    press_to_continue()

    al1 = create_alias(
        client,
        connection_id,
        name="sales",
        target_name="orders",
        target_type="table",
        description="Sales orders table"
    )
    press_to_continue()

    # Example: customers table
    print("\n  Creating alias for customers table...")
    press_to_continue()

    al2 = create_alias(
        client,
        connection_id,
        name="users",
        target_name="customers",
        target_type="table",
        description="Users/customers table"
    )
    press_to_continue()

    # Step 4: Create column aliases
    print("\n[Step 4] Create column aliases")
    print("  Mapping business terms to column names")

    print("\n  Creating alias for amount column...")
    press_to_continue()

    al3 = create_alias(
        client,
        connection_id,
        name="revenue",
        target_name="amount",
        target_type="column",
        description="Revenue/sales amount"
    )
    press_to_continue()

    print("\n  Creating alias for created_at column...")
    press_to_continue()

    al4 = create_alias(
        client,
        connection_id,
        name="date",
        target_name="created_at",
        target_type="column",
        description="Order date or creation timestamp"
    )
    press_to_continue()

    # Step 5: List all aliases
    print("\n[Step 5] List all aliases")
    all_aliases = list_aliases(client, connection_id)
    press_to_continue()

    # Step 6: Filter by target type
    print("\n[Step 6] Filter aliases by target type")
    print("\n  Table aliases:")
    list_aliases(client, connection_id, "table")
    press_to_continue()

    print("\n  Column aliases:")
    list_aliases(client, connection_id, "column")
    press_to_continue()

    # Step 7: Find alias by name
    print("\n[Step 7] Find alias by name")
    found = get_alias_by_name(client, "sales", connection_id)
    press_to_continue()

    # Step 8: Get specific alias
    print("\n[Step 8] Get specific alias details")
    if al1:
        details = get_alias(client, al1["id"])
        print(f"  Name: {details['name']}")
        print(f"  Target: {details['target_type']}.{details['target_name']}")
        print(f"  Description: {details.get('description', 'N/A')}")
    press_to_continue()

    # Step 9: Update alias
    print("\n[Step 9] Update an alias")
    if al1:
        print("  Updating the 'sales' alias description...")
        press_to_continue()

        updated = update_alias(
            client,
            al1["id"],
            description="Sales orders and transactions table"
        )
        print_response(updated, "Updated Alias")
    press_to_continue()

    # Step 10: Cleanup
    print("\n[Step 10] Cleanup")
    print("  Created aliases can be deleted.")

    all_aliases = list_aliases(client, connection_id)
    if all_aliases:
        if should_cleanup:
            print("  --cleanup enabled: Deleting created resources.")
            for al in all_aliases:
                if al.get("metadata", {}).get("created_by") == "cookbook":
                    delete_alias(client, al["id"])
        else:
            print("  --no-cleanup: Preserving created resources.")
            print("  Run with --cleanup flag to remove created resources.")

    print_section("Demo Complete")
    print("\nKey Concepts:")
    print("  - Aliases map business terminology to technical names")
    print("  - They help natural language queries use familiar terms")
    print("  - Use table aliases for business entity names")
    print("  - Use column aliases for business metric names")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
