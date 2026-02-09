#!/usr/bin/env python3
"""
KAI Cookbook - Basic 05: Create Context Stores

This script demonstrates how to create and manage context stores in KAI.
Context stores provide example SQL queries for similar prompts, improving SQL generation.

API Endpoints:
- POST /api/v1/context-stores - Create a new context store
- GET /api/v1/context-stores - List context stores (filtered by connection)
- GET /api/v1/context-stores/{id} - Get a specific context store
- POST /api/v1/context-stores/get-by-prompt - Find context stores by prompt text
- POST /api/v1/context-stores/semantic-search - Semantic search for relevant contexts
- DELETE /api/v1/context-stores/{id} - Delete a context store

Context Stores Structure:
- prompt_text: The example prompt/query text
- sql: The corresponding SQL query
- NER labels and entities are auto-extracted from the prompt
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


def list_context_stores(client: KAIAPIClient, connection_id: str) -> list:
    """List all context stores for a connection."""
    print_subsection("Listing context stores")

    context_stores = client.get("/context-stores", params={"db_connection_id": connection_id})

    if not context_stores:
        print("  No context stores found.")
        return []

    print(f"  Found {len(context_stores)} context store(s):")
    for ctx in context_stores[:5]:
        print(f"    - ID: {ctx['id']}")
        print(f"      Prompt: {ctx['prompt_text'][:50]}...")
        print(f"      SQL: {ctx['sql'][:50]}...")
        if ctx.get('entities'):
            print(f"      Entities: {', '.join(ctx.get('entities', [])[:3])}")
        print()

    if len(context_stores) > 5:
        print(f"  ... and {len(context_stores) - 5} more")

    return context_stores


def create_context_store(
    client: KAIAPIClient,
    connection_id: str,
    prompt_text: str,
    sql: str,
) -> dict:
    """Create a new context store entry."""
    print_subsection("Creating context store")

    payload = {
        "db_connection_id": connection_id,
        "prompt_text": prompt_text,
        "sql": sql,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Prompt: {prompt_text}")
    print(f"  SQL: {sql}")

    context_store = client.post("/context-stores", json_data=payload)
    print(f"  ✓ Context store created: {context_store['id']}")

    # Show extracted NER info
    if context_store.get('entities'):
        print(f"  Extracted entities: {context_store['entities']}")
    if context_store.get('labels'):
        print(f"  Labels: {context_store['labels']}")

    return context_store


def find_context_by_prompt(
    client: KAIAPIClient,
    connection_id: str,
    prompt_text: str,
) -> list:
    """Find context stores that match a given prompt."""
    print_subsection(f"Finding context for: {prompt_text[:40]}...")

    payload = {
        "db_connection_id": connection_id,
        "prompt_text": prompt_text
    }

    results = client.post("/context-stores/get-by-prompt", json_data=payload)

    if not results:
        print("  No matching context found.")
        return []

    print(f"  Found {len(results)} matching context(s):")
    for ctx in results:
        print(f"    - Prompt: {ctx['prompt_text'][:50]}...")
        print(f"      SQL: {ctx['sql'][:60]}...")

    return results


def semantic_search_contexts(
    client: KAIAPIClient,
    connection_id: str,
    prompt_text: str,
    top_k: int = 3,
) -> list:
    """Semantically search for relevant context stores."""
    print_subsection(f"Semantic search for: {prompt_text[:40]}...")

    payload = {
        "db_connection_id": connection_id,
        "prompt_text": prompt_text,
        "top_k": top_k
    }

    results = client.post("/context-stores/semantic-search", json_data=payload)

    if not results:
        print("  No relevant context found.")
        return []

    print(f"  Found {len(results)} relevant context(s):")
    for i, ctx in enumerate(results, 1):
        print(f"    {i}. Score: {ctx.get('score', 'N/A')}")
        print(f"       Prompt: {ctx.get('prompt_text', 'N/A')[:50]}...")
        print(f"       SQL: {ctx.get('sql', 'N/A')[:60]}...")

    return results


def get_context_store(client: KAIAPIClient, context_store_id: str) -> dict:
    """Get a specific context store."""
    print_subsection(f"Getting context store: {context_store_id}")
    context_store = client.get(f"/context-stores/{context_store_id}")
    return context_store


def delete_context_store(client: KAIAPIClient, context_store_id: str) -> None:
    """Delete a context store."""
    print_subsection(f"Deleting context store: {context_store_id}")
    result = client.delete(f"/context-stores/{context_store_id}")
    print(f"  ✓ Deleted: {result.get('message', 'Success')}")


def main() -> None:
    """Main execution function."""
    # Parse command-line arguments first (before any print statements)
    args = parse_cookbook_args()
    should_cleanup = not args.no_cleanup

    print_section("KAI Cookbook - Basic 05: Context Stores")

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

    # Step 2: List existing context stores
    print("\n[Step 2] List existing context stores")
    list_context_stores(client, connection_id)
    press_to_continue()

    # Step 3: Create example context stores
    print("\n[Step 3] Create example context stores")

    # Example 1: Sales query
    print("\n  Creating sales context...")
    press_to_continue()

    ctx1 = create_context_store(
        client,
        connection_id,
        "Show me total sales by month",
        "SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) as total FROM orders GROUP BY DATE_TRUNC('month', order_date) ORDER BY month"
    )
    press_to_continue()

    # Example 2: Customer query
    print("\n  Creating customer context...")
    press_to_continue()

    ctx2 = create_context_store(
        client,
        connection_id,
        "List top 10 customers by revenue",
        "SELECT c.name, SUM(o.amount) as revenue FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY revenue DESC LIMIT 10"
    )
    press_to_continue()

    # Example 3: Product query
    print("\n  Creating product context...")
    press_to_continue()

    ctx3 = create_context_store(
        client,
        connection_id,
        "What are our best selling products?",
        "SELECT p.name, SUM(oi.quantity) as total_sold FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.name ORDER BY total_sold DESC LIMIT 10"
    )
    press_to_continue()

    # Step 4: List all context stores
    print("\n[Step 4] List all context stores")
    all_contexts = list_context_stores(client, connection_id)
    press_to_continue()

    # Step 5: Find context by prompt
    print("\n[Step 5] Find context by prompt matching")
    find_context_by_prompt(
        client,
        connection_id,
        "I want to see the monthly sales figures"
    )
    press_to_continue()

    # Step 6: Semantic search
    print("\n[Step 6] Semantic search for relevant contexts")
    semantic_search_contexts(
        client,
        connection_id,
        "Which products sell the most?",
        top_k=2
    )
    press_to_continue()

    # Step 7: Get specific context store
    print("\n[Step 7] Get specific context store details")
    if ctx1:
        details = get_context_store(client, ctx1["id"])
        print(f"  Prompt: {details['prompt_text']}")
        print(f"  SQL: {details['sql']}")
        print(f"  Entities: {details.get('entities', [])}")
        print(f"  Labels: {details.get('labels', [])}")
    press_to_continue()

    # Step 8: Cleanup
    print("\n[Step 8] Cleanup")
    print("  Created context stores can be deleted.")

    all_contexts = list_context_stores(client, connection_id)
    if all_contexts:
        if should_cleanup:
            print("  --cleanup enabled: Deleting created resources.")
            for ctx in all_contexts:
                if ctx.get("metadata", {}).get("created_by") == "cookbook":
                    delete_context_store(client, ctx["id"])
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
