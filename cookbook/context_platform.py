#!/usr/bin/env python3
"""
KAI Cookbook - Context Platform

This script demonstrates how to use the Context Platform for managing
domain knowledge assets through their lifecycle (draft → verified → published → deprecated).

API Endpoints:
- POST /api/v1/context/assets - Create a new context asset
- GET /api/v1/context/assets - List context assets
- GET /api/v1/context/assets/{id} - Get a specific asset
- PATCH /api/v1/context/assets/{id} - Update an asset
- POST /api/v1/context/assets/{id}/promote - Promote to next lifecycle state
- POST /api/v1/context/assets/{id}/deprecate - Deprecate an asset
- DELETE /api/v1/context/assets/{db}/{type}/{key} - Delete an asset
- POST /api/v1/context/assets/search - Search assets by query
- GET /api/v1/context/tags - List all tags

Context Asset Types:
- table_description: Descriptive metadata about database tables
- glossary: Business terminology and definitions
- instruction: Domain-specific analysis rules
- skill: Reusable analysis patterns

Lifecycle States:
- draft: Initial creation
- verified: Reviewed by domain expert
- published: Approved for reuse
- deprecated: Superseded or obsolete
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


def list_context_assets(
    client: KAIAPIClient,
    connection_id: str,
    asset_type: str | None = None,
    lifecycle_state: str | None = None,
) -> list:
    """List context assets for a connection."""
    print_subsection("Listing context assets")

    params = {"db_connection_id": connection_id}
    if asset_type:
        params["asset_type"] = asset_type
    if lifecycle_state:
        params["lifecycle_state"] = lifecycle_state

    assets = client.get("/context/assets", params=params)

    if not assets:
        print("  No context assets found.")
        return []

    print(f"  Found {len(assets)} asset(s):")
    for asset in assets[:5]:
        print(f"    - ID: {asset['id']}")
        print(f"      Type: {asset['asset_type']}")
        print(f"      Key: {asset['canonical_key']}")
        print(f"      Name: {asset['name']}")
        print(f"      State: {asset['lifecycle_state']}")
        print(f"      Version: {asset['version']}")
        print()

    if len(assets) > 5:
        print(f"  ... and {len(assets) - 5} more")

    return assets


def create_context_asset(
    client: KAIAPIClient,
    connection_id: str,
    asset_type: str,
    canonical_key: str,
    name: str,
    content: dict,
    description: str | None = None,
    tags: list[str] | None = None,
    author: str | None = None,
) -> dict:
    """Create a new context asset."""
    print_subsection("Creating context asset")

    payload = {
        "db_connection_id": connection_id,
        "asset_type": asset_type,
        "canonical_key": canonical_key,
        "name": name,
        "content": content,
        "content_text": str(content),
    }

    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags
    if author:
        payload["author"] = author

    print(f"  Type: {asset_type}")
    print(f"  Key: {canonical_key}")
    print(f"  Name: {name}")
    print(f"  Tags: {tags or []}")

    asset = client.post("/context/assets", json_data=payload)
    print(f"  ✓ Context asset created: {asset['id']}")
    print(f"    State: {asset['lifecycle_state']}")

    return asset


def show_context_asset(client: KAIAPIClient, asset_id: str) -> dict:
    """Show details of a context asset."""
    print_subsection(f"Showing context asset: {asset_id}")

    asset = client.get(f"/context/assets/{asset_id}")

    print(f"  ID: {asset['id']}")
    print(f"  Type: {asset['asset_type']}")
    print(f"  Key: {asset['canonical_key']}")
    print(f"  Name: {asset['name']}")
    print(f"  Description: {asset.get('description', 'N/A')}")
    print(f"  State: {asset['lifecycle_state']}")
    print(f"  Version: {asset['version']}")
    print(f"  Tags: {asset.get('tags', [])}")
    print(f"  Author: {asset.get('author', 'N/A')}")
    print(f"  Created: {asset.get('created_at', 'N/A')}")
    print(f"  Updated: {asset.get('updated_at', 'N/A')}")

    if asset.get("content"):
        print(f"  Content: {asset['content']}")

    return asset


def update_context_asset(
    client: KAIAPIClient,
    asset_id: str,
    name: str | None = None,
    description: str | None = None,
    content: dict | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update a context asset."""
    print_subsection(f"Updating context asset: {asset_id}")

    # Get current asset first
    current = client.get(f"/context/assets/{asset_id}")

    payload = {}
    if name:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if content is not None:
        payload["content"] = content
        payload["content_text"] = str(content)
    if tags is not None:
        payload["tags"] = tags

    asset = client.patch(f"/context/assets/{asset_id}", json_data=payload)
    print(f"  ✓ Context asset updated")
    print(f"    Name: {asset['name']}")

    return asset


def promote_context_asset(
    client: KAIAPIClient,
    asset_id: str,
    target_state: str,
    promoted_by: str,
    change_note: str | None = None,
) -> dict:
    """Promote a context asset to the next lifecycle state."""
    print_subsection(f"Promoting asset to {target_state}")

    payload = {
        "target_state": target_state,
        "promoted_by": promoted_by,
    }
    if change_note:
        payload["change_note"] = change_note

    print(f"  Target state: {target_state}")
    print(f"  Promoted by: {promoted_by}")

    asset = client.post(f"/context/assets/{asset_id}/promote", json_data=payload)
    print(f"  ✓ Asset promoted to {target_state}")
    print(f"    New state: {asset['lifecycle_state']}")

    return asset


def deprecate_context_asset(
    client: KAIAPIClient,
    asset_id: str,
    deprecated_by: str,
    reason: str,
) -> dict:
    """Deprecate a context asset."""
    print_subsection(f"Deprecating asset: {asset_id}")

    payload = {
        "deprecated_by": deprecated_by,
        "reason": reason,
    }

    print(f"  Reason: {reason}")

    asset = client.post(f"/context/assets/{asset_id}/deprecate", json_data=payload)
    print(f"  ✓ Asset deprecated")
    print(f"    New state: {asset['lifecycle_state']}")

    return asset


def search_context_assets(
    client: KAIAPIClient,
    connection_id: str,
    query: str,
    limit: int = 10,
) -> list:
    """Search context assets by query."""
    print_subsection(f"Searching for: {query[:40]}...")

    payload = {
        "db_connection_id": connection_id,
        "query": query,
        "limit": limit,
    }

    results = client.post("/context/assets/search", json_data=payload)

    if not results:
        print("  No results found.")
        return []

    print(f"  Found {len(results)} result(s):")
    for i, result in enumerate(results, 1):
        asset = result.get("asset", result)
        score = result.get("score", 0)
        print(f"    {i}. Score: {score:.2f}")
        print(f"       Type: {asset.get('asset_type', 'N/A')}")
        print(f"       Key: {asset.get('canonical_key', 'N/A')}")
        print(f"       Name: {asset.get('name', 'N/A')[:50]}")

    return results


def list_tags(client: KAIAPIClient, category: str | None = None) -> list:
    """List all context asset tags."""
    print_subsection("Listing tags")

    params = {}
    if category:
        params["category"] = category

    tags = client.get("/context/tags", params=params)

    if not tags:
        print("  No tags found.")
        return []

    print(f"  Found {len(tags)} tag(s):")
    for tag in tags:
        print(f"    - {tag['name']}")
        print(f"      Category: {tag.get('category', 'none')}")
        print(f"      Usage: {tag.get('usage_count', 0)}")

    return tags


def delete_context_asset(
    client: KAIAPIClient,
    connection_id: str,
    asset_type: str,
    canonical_key: str,
) -> None:
    """Delete a context asset."""
    print_subsection(f"Deleting asset: {asset_type}/{canonical_key}")

    result = client.delete(f"/context/assets/{connection_id}/{asset_type}/{canonical_key}")
    print(f"  ✓ Asset deleted")

    return result


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Context Platform")

    client = KAIAPIClient()

    # Use sample database from environment
    example_alias = SAMPLE_DB_ALIAS
    print(f"\nUsing connection alias: {example_alias}")
    press_to_continue("Press Enter to continue or Ctrl+C to cancel...")

    # Step 1: Get connection ID
    print("\n[Step 1] Get connection ID")
    connection_id = get_connection_id_by_alias(client, example_alias)

    if not connection_id:
        print(f"  ✗ Connection '{example_alias}' not found!")
        return

    print(f"  ✓ Found connection: {example_alias}")
    press_to_continue()

    # Step 2: List existing context assets
    print("\n[Step 2] List existing context assets")
    existing_assets = list_context_assets(client, connection_id)
    press_to_continue()

    # Step 3: Create a glossary asset
    print("\n[Step 3] Create glossary asset")
    glossary_content = {
        "metrics": [
            {
                "name": "Gross Margin",
                "definition": "Revenue minus Cost of Goods Sold, divided by Revenue",
                "sql_template": "SELECT SUM(revenue - cost) / SUM(revenue) FROM sales"
            },
            {
                "name": "YTD Sales",
                "definition": "Year-to-Date sales from fiscal year start",
                "sql_template": "SELECT SUM(amount) WHERE date >= fiscal_year_start"
            },
        ]
    }

    glossary = create_context_asset(
        client,
        connection_id,
        "glossary",
        "financial_metrics",
        "Financial Metrics Glossary",
        glossary_content,
        description="Standard financial metric definitions",
        tags=["finance", "metrics", "sales"],
        author="cookbook",
    )
    press_to_continue()

    # Step 4: Create an instruction asset
    print("\n[Step 4] Create instruction asset")
    instruction_content = {
        "condition": "When user asks about YTD (Year-to-Date)",
        "rules": [
            "Always use fiscal_year_start from config table",
            "Filter by date >= fiscal_year_start",
            "Never use calendar year boundaries",
        ],
        "examples": [
            {
                "query": "YTD sales",
                "expected_behavior": "Use fiscal year start date"
            },
        ],
    }

    instruction = create_context_asset(
        client,
        connection_id,
        "instruction",
        "ytd_rules",
        "YTD Analysis Rules",
        instruction_content,
        description="Rules for year-to-date calculations",
        tags=["finance", "reporting", "rules"],
        author="cookbook",
    )
    press_to_continue()

    # Step 5: Promote glossary to verified
    print("\n[Step 5] Promote glossary to verified")
    promote_context_asset(
        client,
        glossary["id"],
        "verified",
        "Domain Expert",
        change_note="Reviewed and validated financial metrics",
    )
    press_to_continue()

    # Step 6: Promote instruction to verified
    print("\n[Step 6] Promote instruction to verified")
    promote_context_asset(
        client,
        instruction["id"],
        "verified",
        "Domain Expert",
        change_note="Validated YTD analysis rules",
    )
    press_to_continue()

    # Step 7: Promote glossary to published
    print("\n[Step 7] Promote glossary to published")
    promote_context_asset(
        client,
        glossary["id"],
        "published",
        "Tech Lead",
        change_note="Approved for production use",
    )
    press_to_continue()

    # Step 8: List all assets
    print("\n[Step 8] List all context assets")
    all_assets = list_context_assets(client, connection_id)
    press_to_continue()

    # Step 9: Search for assets
    print("\n[Step 9] Search for assets")
    search_context_assets(client, connection_id, "financial metrics", limit=5)
    press_to_continue()

    # Step 10: List tags
    print("\n[Step 10] List all tags")
    list_tags(client)
    press_to_continue()

    # Step 11: Show asset details
    print("\n[Step 11] Show asset details")
    show_context_asset(client, glossary["id"])
    press_to_continue()

    # Step 12: Update asset
    print("\n[Step 12] Update asset")
    updated_glossary = update_context_asset(
        client,
        glossary["id"],
        name="Financial Metrics Glossary v2",
    )
    press_to_continue()

    # Step 13: Deprecate asset
    print("\n[Step 13] Deprecate asset")
    deprecate_context_asset(
        client,
        instruction["id"],
        "Tech Lead",
        "Replaced by new version of YTD rules",
    )
    press_to_continue()

    # Step 14: Cleanup
    print("\n[Step 14] Cleanup")
    print("  Created assets can be deleted.")

    if should_cleanup:
        print("  --cleanup enabled: Deleting created resources.")
        # Delete the assets we created
        try:
            delete_context_asset(client, connection_id, "glossary", "financial_metrics")
            delete_context_asset(client, connection_id, "instruction", "ytd_rules")
        except Exception as e:
            print(f"  Note: Cleanup encountered issues: {e}")
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
