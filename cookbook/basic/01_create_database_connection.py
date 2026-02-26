#!/usr/bin/env python3
"""
KAI Cookbook - Basic 01: Create Database Connection

This script demonstrates how to create and manage database connections in KAI.

API Endpoints:
- POST /api/v1/database-connections - Create a new database connection
- GET /api/v1/database-connections - List all database connections
- PUT /api/v1/database-connections/{id} - Update a database connection
- DELETE /api/v1/database-connections/{id} - Delete a database connection
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    KAIAPIClient,
    SAMPLE_DB_URI,
    SAMPLE_DB_ALIAS,
    parse_cookbook_args,
    print_section,
    print_subsection,
    print_response,
    press_to_continue,
    find_by_name,
)


def list_connections(client: KAIAPIClient) -> list[dict]:
    """List all database connections."""
    print_subsection("Listing all database connections")
    connections = client.get("/database-connections")

    if not connections:
        print("  No database connections found.")
        return []

    print(f"  Found {len(connections)} connection(s):")
    for conn in connections:
        print(f"    - ID: {conn['id']}")
        print(f"      Alias: {conn['alias']}")
        print(f"      Connection URI: {conn['connection_uri'][:30]}...")
        print(f"      Schemas: {conn.get('schemas', [])}")
        print()

    return connections


def create_connection(
    client: KAIAPIClient,
    alias: str,
    connection_uri: str,
    schemas: list[str] | None = None,
) -> dict:
    """Create a new database connection."""
    print_subsection(f"Creating database connection: {alias}")

    payload = {
        "alias": alias,
        "connection_uri": connection_uri,
        "schemas": schemas,
        "metadata": {"created_by": "cookbook", "example": True}
    }

    connection = client.post("/database-connections", json_data=payload)
    print(f"  ✓ Connection created successfully!")
    print(f"    ID: {connection['id']}")
    print(f"    Alias: {connection['alias']}")

    return connection


def get_connection(client: KAIAPIClient, alias: str) -> dict | None:
    """Get an existing connection by alias."""
    connections = list_connections(client)
    return find_by_name(connections, alias, "alias")


def update_connection(
    client: KAIAPIClient,
    connection_id: str,
    new_alias: str | None = None,
    new_uri: str | None = None,
) -> dict:
    """Update an existing database connection."""
    print_subsection(f"Updating connection: {connection_id}")

    # Get current connection first
    current = client.get(f"/database-connections/{connection_id}")

    payload = {
        "alias": new_alias or current["alias"],
        "connection_uri": new_uri or current["connection_uri"],
        "schemas": current.get("schemas"),
        "metadata": current.get("metadata", {})
    }

    updated = client.put(f"/database-connections/{connection_id}", json_data=payload)
    print(f"  ✓ Connection updated successfully!")
    print(f"    ID: {updated['id']}")
    print(f"    Alias: {updated['alias']}")

    return updated


def delete_connection(client: KAIAPIClient, connection_id: str) -> None:
    """Delete a database connection."""
    print_subsection(f"Deleting connection: {connection_id}")
    result = client.delete(f"/database-connections/{connection_id}")
    print(f"  ✓ Connection deleted: {result.get('message', 'Success')}")


def main() -> None:
    """Main execution function."""
    print_section("KAI Cookbook - Basic 01: Database Connection Management")

    # Initialize API client
    client = KAIAPIClient()

    # Use sample database from environment (.env file)
    # This is the Kementerian Koperasi database hosted on Neon
    print(f"\nUsing sample database: {SAMPLE_DB_ALIAS}")
    print("  (from SAMPLE_DB_URI in .env)")

    # Step 1: List existing connections
    print("\n[Step 1] List existing database connections")
    list_connections(client)
    press_to_continue()

    # Step 2: Check if demo connection already exists
    print("\n[Step 2] Check for existing demo connection")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing:
        print(f"  ℹ Sample connection '{SAMPLE_DB_ALIAS}' already exists.")
        print(f"     ID: {existing['id']}")
        press_to_continue()
    else:
        # Step 3: Create a new connection
        print("\n[Step 3] Create new database connection")
        print(f"  Connecting to Kementerian Koperasi database (Neon)")
        press_to_continue("Press Enter to create the connection or Ctrl+C to cancel...")

        try:
            connection = create_connection(client, SAMPLE_DB_ALIAS, SAMPLE_DB_URI, ["public"])
            print_response(connection, "Created Connection")
        except Exception as e:
            print(f"  ✗ Failed to create connection: {e}")
            print(f"  Make sure the database is accessible and credentials are correct.")
            return
        press_to_continue()

    # Step 4: List connections again to verify
    print("\n[Step 4] Verify connection was created")
    list_connections(client)
    press_to_continue()

    # Step 5: Update the connection (optional demo)
    print("\n[Step 5] Update connection metadata")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing:
        print("  Note: This demonstrates updating a connection.")
        print("  In this example, we'll update the metadata.")
        press_to_continue()

        current = client.get(f"/database-connections/{existing['id']}")
        updated_metadata = current.get("metadata", {})
        updated_metadata["updated_by"] = "cookbook_update_example"
        updated_metadata["source"] = "kementerian_koperasi"

        update_connection(
            client,
            existing["id"],
            new_uri=current["connection_uri"]
        )
        press_to_continue()

    # Step 6: Cleanup option
    print("\n[Step 6] Cleanup")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing and should_cleanup:
        print("  --cleanup enabled: Deleting the sample connection.")
        delete_connection(client, existing["id"])
    else:
        print("  Connection kept for use by other cookbook scripts.")
        print("  Run with --cleanup flag to remove created resources.")

    print_section("Demo Complete")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    if args.no_cleanup:
        print("Note: Running with --no-cleanup. Resources will be preserved.")
    else:
        print("Note: Running with cleanup enabled. Resources will be deleted at the end.")
    press_to_continue("Press Enter to continue or Ctrl+C to cancel...")

    print_section("KAI Cookbook - Basic 01: Database Connection Management")

    # Initialize API client
    client = KAIAPIClient()

    # Use sample database from environment (.env file)
    # This is the Kementerian Koperasi database hosted on Neon
    print(f"\nUsing sample database: {SAMPLE_DB_ALIAS}")
    print("  (from SAMPLE_DB_URI in .env)")

    # Step 1: List existing connections
    print("\n[Step 1] List existing database connections")
    list_connections(client)
    press_to_continue()

    # Step 2: Check if demo connection already exists
    print("\n[Step 2] Check for existing demo connection")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing:
        print(f"  ℹ Sample connection '{SAMPLE_DB_ALIAS}' already exists.")
        print(f"     ID: {existing['id']}")
        press_to_continue()
    else:
        # Step 3: Create a new connection
        print("\n[Step 3] Create new database connection")
        print(f"  Connecting to Kementerian Koperasi database (Neon)")
        press_to_continue("Press Enter to create the connection or Ctrl+C to cancel...")

        try:
            connection = create_connection(client, SAMPLE_DB_ALIAS, SAMPLE_DB_URI, ["public"])
            print_response(connection, "Created Connection")
        except Exception as e:
            print(f"  ✗ Failed to create connection: {e}")
            print(f"  Make sure the database is accessible and credentials are correct.")
            return
        press_to_continue()

    # Step 4: List connections again to verify
    print("\n[Step 4] Verify connection was created")
    list_connections(client)
    press_to_continue()

    # Step 5: Update the connection (optional demo)
    print("\n[Step 5] Update connection metadata")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing:
        print("  Note: This demonstrates updating a connection.")
        print("  In this example, we'll update the metadata.")
        press_to_continue()

        current = client.get(f"/database-connections/{existing['id']}")
        updated_metadata = current.get("metadata", {})
        updated_metadata["updated_by"] = "cookbook_update_example"
        updated_metadata["source"] = "kementerian_koperasi"

        update_connection(
            client,
            existing["id"],
            new_uri=current["connection_uri"]
        )
        press_to_continue()

    # Step 6: Cleanup option
    print("\n[Step 6] Cleanup")
    existing = get_connection(client, SAMPLE_DB_ALIAS)
    if existing and should_cleanup:
        print("  --cleanup enabled: Deleting the sample connection.")
        delete_connection(client, existing["id"])
    else:
        print("  Connection kept for use by other cookbook scripts.")
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
