#!/usr/bin/env python3
"""
KAI Cookbook - Basic 04: Create Instructions

This script demonstrates how to create and manage instructions in KAI.
Instructions are rules that guide SQL generation for specific query conditions.

API Endpoints:
- POST /api/v1/instructions - Create a new instruction
- GET /api/v1/instructions - List instructions (filtered by connection)
- GET /api/v1/instructions/{id} - Get a specific instruction
- PUT /api/v1/instructions/{id} - Update an instruction
- DELETE /api/v1/instructions/{id} - Delete an instruction

Instructions Structure:
- condition: When this instruction applies (e.g., "contains 'revenue'")
- rules: What rules to apply (e.g., "use SUM(amount)")
- is_default: Whether this is a default instruction
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


def list_instructions(client: KAIAPIClient, connection_id: str) -> list:
    """List all instructions for a connection."""
    print_subsection("Listing instructions")

    instructions = client.get("/instructions", params={"db_connection_id": connection_id})

    if not instructions:
        print("  No instructions found.")
        return []

    print(f"  Found {len(instructions)} instruction(s):")
    for instr in instructions:
        default_mark = " [DEFAULT]" if instr.get("is_default") else ""
        print(f"    - ID: {instr['id']}{default_mark}")
        print(f"      Condition: {instr['condition'][:50]}...")
        print(f"      Rules: {instr['rules'][:50]}...")
        print()

    return instructions


def create_instruction(
    client: KAIAPIClient,
    connection_id: str,
    condition: str,
    rules: str,
    is_default: bool = False,
) -> dict:
    """Create a new instruction."""
    print_subsection("Creating instruction")

    payload = {
        "db_connection_id": connection_id,
        "condition": condition,
        "rules": rules,
        "is_default": is_default,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Condition: {condition}")
    print(f"  Rules: {rules}")
    print(f"  Is Default: {is_default}")

    instruction = client.post("/instructions", json_data=payload)
    print(f"  ✓ Instruction created: {instruction['id']}")

    return instruction


def get_instruction(client: KAIAPIClient, instruction_id: str) -> dict:
    """Get a specific instruction."""
    print_subsection(f"Getting instruction: {instruction_id}")
    instruction = client.get(f"/instructions/{instruction_id}")
    return instruction


def update_instruction(
    client: KAIAPIClient,
    instruction_id: str,
    condition: str | None = None,
    rules: str | None = None,
    is_default: bool | None = None,
) -> dict:
    """Update an instruction."""
    print_subsection(f"Updating instruction: {instruction_id}")

    # Get current instruction
    current = client.get(f"/instructions/{instruction_id}")

    payload = {}
    if condition is not None:
        payload["condition"] = condition
    if rules is not None:
        payload["rules"] = rules
    if is_default is not None:
        payload["is_default"] = is_default

    updated = client.put(f"/instructions/{instruction_id}", json_data=payload)
    print(f"  ✓ Instruction updated")

    return updated


def delete_instruction(client: KAIAPIClient, instruction_id: str) -> None:
    """Delete an instruction."""
    print_subsection(f"Deleting instruction: {instruction_id}")
    result = client.delete(f"/instructions/{instruction_id}")
    print(f"  ✓ Deleted: {result.get('message', 'Success')}")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 04: Instructions")

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

    # Step 2: List existing instructions
    print("\n[Step 2] List existing instructions")
    list_instructions(client, connection_id)
    press_to_continue()

    # Step 3: Create example instructions
    print("\n[Step 3] Create example instructions")

    # Example 1: Revenue calculation instruction (conditional)
    print("\n  Creating revenue calculation instruction...")
    print("  This instruction applies when user asks about revenue (is_default=False)")
    press_to_continue()

    instruction1 = create_instruction(
        client,
        connection_id,
        condition="user asks about revenue, sales, or income",
        rules="Use SUM(amount * quantity) for revenue calculations. Group by date when analyzing trends.",
        is_default=False  # Conditional instruction with embedding for semantic matching
    )
    print_response(instruction1, "Created Instruction 1")
    press_to_continue()

    # Example 2: Date filtering instruction (conditional)
    print("\n  Creating date filtering instruction...")
    print("  This instruction applies for queries with date filters (is_default=False)")
    press_to_continue()

    instruction2 = create_instruction(
        client,
        connection_id,
        condition="query contains date or time filter",
        rules="Always use proper date casting. For PostgreSQL, use column_name::DATE or DATE(column_name).",
        is_default=False  # Conditional instruction with embedding for semantic matching
    )
    print_response(instruction2, "Created Instruction 2")
    press_to_continue()

    # Example 3: Default instruction
    print("\n  Creating default instruction...")
    press_to_continue()

    instruction3 = create_instruction(
        client,
        connection_id,
        condition="always",
        rules="Limit results to 100 rows by default. Use ORDER BY for consistent results.",
        is_default=True
    )
    print_response(instruction3, "Created Instruction 3 (Default)")
    press_to_continue()

    # Step 4: List all instructions again
    print("\n[Step 4] List all instructions")
    all_instructions = list_instructions(client, connection_id)
    press_to_continue()

    # Step 5: Get specific instruction
    print("\n[Step 5] Get specific instruction details")
    if instruction1:
        details = get_instruction(client, instruction1["id"])
        print(f"  Condition: {details['condition']}")
        print(f"  Rules: {details['rules']}")
        print(f"  Is Default: {details.get('is_default', False)}")
    press_to_continue()

    # Step 6: Update instruction
    print("\n[Step 6] Update an instruction")
    if instruction1:
        print("  Updating instruction 1...")
        print("  Note: Update regenerates the embedding with new condition/rules")
        press_to_continue()

        try:
            updated = update_instruction(
                client,
                instruction1["id"],
                condition="user asks about revenue, sales, turnover, or total income",
                rules="Use SUM(amount * quantity) as revenue. Group by month for monthly reports."
            )
            print_response(updated, "Updated Instruction")
        except Exception as e:
            print(f"  ! Update failed: {e}")
    press_to_continue()

    # Step 7: Cleanup
    print("\n[Step 7] Cleanup")
    print("  Created instructions can be deleted.")

    all_instructions = list_instructions(client, connection_id)
    if all_instructions:
        if should_cleanup:
            print("  --cleanup enabled: Deleting created resources.")
            for instr in all_instructions:
                if instr.get("metadata", {}).get("created_by") == "cookbook":
                    delete_instruction(client, instr["id"])
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
