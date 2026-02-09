#!/usr/bin/env python3
"""
KAI Cookbook - Advanced 03: RAG Documents

This script demonstrates how to use KAI's RAG (Retrieval Augmented Generation)
capabilities for document-based knowledge retrieval.

API Endpoints:
- POST /api/v1/rags/upload-document - Upload and parse a PDF document
- POST /api/v1/rags/create-document - Create a document from text
- GET /api/v1/rags/documents - List all documents
- GET /api/v1/rags/documents/{id} - Get a specific document
- DELETE /api/v1/rags/documents/{id} - Delete a document
- POST /api/v1/rags/embeddings/ - Create embeddings for a document
- GET /api/v1/rags/embeddings/ - Retrieve knowledge (semantic search)

RAG Features:
- Document storage and indexing
- Vector embeddings for semantic search
- Knowledge retrieval based on natural language queries
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    KAIAPIClient,
    print_section,
    print_subsection,
    print_response,
    press_to_continue,
)


def create_document_from_text(
    client: KAIAPIClient,
    title: str,
    text_content: str,
    content_type: str = "text",
) -> dict:
    """Create a document from text content."""
    print_subsection(f"Creating document: {title}")

    payload = {
        "title": title,
        "content_type": content_type,
        "text_content": text_content,
        "metadata": {"created_by": "cookbook"}
    }

    print(f"  Title: {title}")
    print(f"  Content length: {len(text_content)} characters")

    document = client.post("/rags/create-document", json_data=payload)
    print(f"  ✓ Document created: {document['id']}")

    return document


def list_documents(client: KAIAPIClient) -> list:
    """List all documents."""
    print_subsection("Listing documents")

    documents = client.get("/rags/documents")

    if not documents:
        print("  No documents found.")
        return []

    print(f"  Found {len(documents)} document(s):")
    for doc in documents:
        print(f"    - ID: {doc['id']}")
        print(f"      Title: {doc.get('title', 'N/A')}")
        print(f"      Type: {doc.get('content_type', 'N/A')}")
        print(f"      Size: {doc.get('document_size', 0)} bytes")
        print()

    return documents


def get_document(client: KAIAPIClient, document_id: str) -> dict:
    """Get a specific document."""
    print_subsection(f"Getting document: {document_id}")
    document = client.get(f"/rags/documents/{document_id}")
    return document


def embed_document(client: KAIAPIClient, document_id: str) -> dict:
    """Create embeddings for a document."""
    print_subsection(f"Creating embeddings for document: {document_id}")

    print("  Processing document and creating vector embeddings...")

    result = client.post(f"/rags/embeddings/", json_data={"document_id": document_id})

    print(f"  ✓ Embeddings created")
    return result


def retrieve_knowledge(client: KAIAPIClient, query: str) -> dict:
    """Retrieve knowledge based on a query."""
    print_subsection(f"Retrieving knowledge for: {query}")

    print(f"  Query: {query}")
    print("  Searching embeddings...")

    result = client.get("/rags/embeddings/", params={"query": query})

    print(f"  Final Answer: {result.get('Final Answer', 'N/A')[:200]}...")

    if result.get('input_tokens_used'):
        print(f"  Input Tokens: {result['input_tokens_used']}")
    if result.get('output_tokens_used'):
        print(f"  Output Tokens: {result['output_tokens_used']}")

    return result


def delete_document(client: KAIAPIClient, document_id: str) -> None:
    """Delete a document."""
    print_subsection(f"Deleting document: {document_id}")
    result = client.delete(f"/rags/documents/{document_id}")
    print(f"  ✓ Deleted")


def main() -> None:
    """Main execution function."""
    print_section("KAI Cookbook - Advanced 03: RAG Documents")

    client = KAIAPIClient()

    # Step 1: List existing documents
    print("\n[Step 1] List existing documents")
    list_documents(client)
    press_to_continue()

    # Step 2: Create example documents
    print("\n[Step 2] Create example documents")

    # Example 1: Business documentation
    print("\n  Creating business metrics document...")
    press_to_continue()

    doc1 = create_document_from_text(
        client,
        "Business Metrics Guide",
        """
        # Key Business Metrics

        ## Gross Revenue
        Gross Revenue represents the total income from sales before any deductions.
        Formula: SUM(amount * quantity)
        Common aliases: total sales, income, turnover

        ## Net Revenue
        Net Revenue is Gross Revenue minus returns, discounts, and allowances.
        Formula: SUM(amount * quantity) - SUM(refunds)

        ## Average Order Value (AOV)
        AOV measures the average amount spent per order.
        Formula: SUM(amount) / COUNT(DISTINCT order_id)

        ## Customer Lifetime Value (CLV)
        CLV predicts the total revenue a business can expect from a single customer.
        Formula: SUM(total_revenue) / COUNT(DISTINCT customer_id)

        ## Monthly Recurring Revenue (MRR)
        MRR is the predictable revenue generated from subscriptions.
        Formula: SUM(amount) FILTER (WHERE billing_cycle = 'monthly')
        """.strip()
    )
    press_to_continue()

    # Example 2: Schema documentation
    print("\n  Creating schema documentation...")
    press_to_continue()

    doc2 = create_document_from_text(
        client,
        "Database Schema Reference",
        """
        # Database Schema Reference

        ## orders table
        Contains all customer orders and transactions.
        Key columns:
        - id: Unique order identifier
        - customer_id: Foreign key to customers table
        - amount: Order total amount
        - created_at: Order timestamp
        - status: Order status (pending, completed, cancelled)

        ## customers table
        Contains customer information and profiles.
        Key columns:
        - id: Unique customer identifier
        - name: Customer full name
        - email: Customer email address
        - created_at: Account creation date
        - segment: Customer segment (enterprise, smb, individual)

        ## products table
        Product catalog and inventory.
        Key columns:
        - id: Unique product identifier
        - name: Product name
        - category: Product category
        - price: Unit price
        - stock_quantity: Current inventory level

        ## order_items table
        Line items for each order (junction table).
        Key columns:
        - id: Unique line item identifier
        - order_id: Foreign key to orders
        - product_id: Foreign key to products
        - quantity: Quantity ordered
        - unit_price: Price at time of order
        """.strip()
    )
    press_to_continue()

    # Step 3: List all documents
    print("\n[Step 3] List all documents")
    all_docs = list_documents(client)
    press_to_continue()

    # Step 4: Create embeddings
    print("\n[Step 4] Create embeddings for documents")
    print("  Embeddings enable semantic search on document content")

    if doc1:
        print("\n  Processing document 1...")
        press_to_continue()
        try:
            embed_document(client, doc1["id"])
        except Exception as e:
            print(f"  ! Embedding failed: {e}")
            print("  Make sure embedding service is configured")
    press_to_continue()

    if doc2:
        print("\n  Processing document 2...")
        press_to_continue()
        try:
            embed_document(client, doc2["id"])
        except Exception as e:
            print(f"  ! Embedding failed: {e}")
    press_to_continue()

    # Step 5: Retrieve knowledge
    print("\n[Step 5] Retrieve knowledge from documents")
    print("  Ask questions and get answers from your documents")

    queries = [
        "How do I calculate gross revenue?",
        "What tables do I need for customer orders?",
        "What is the formula for Average Order Value?"
    ]

    for query in queries:
        print(f"\n  Query: {query}")
        press_to_continue("Press Enter to retrieve...")
        try:
            result = retrieve_knowledge(client, query)
            print(f"\n  Answer: {result.get('Final Answer', 'N/A')}")
        except Exception as e:
            print(f"  ! Retrieval failed: {e}")
        press_to_continue()

    # Step 6: Get document details
    print("\n[Step 6] Get document details")
    if doc1:
        details = get_document(client, doc1["id"])
        print(f"  Title: {details.get('title', 'N/A')}")
        print(f"  Size: {details.get('document_size', 0)} bytes")
        print(f"  Content preview: {details.get('text_content', 'N/A')[:100]}...")
    press_to_continue()

    # Step 7: Cleanup
    print("\n[Step 7] Cleanup")
    print("  Created documents can be deleted.")

    all_docs = list_documents(client)
    if all_docs:
        choice = input("  Delete all cookbook documents? (y/N): ").strip().lower()
        if choice == "y":
            for doc in all_docs:
                if doc.get("metadata", {}).get("created_by") == "cookbook":
                    delete_document(client, doc["id"])

    print_section("Demo Complete")
    print("\nKey Concepts:")
    print("  - RAG combines retrieval with generation")
    print("  - Documents are embedded as vectors for semantic search")
    print("  - Query finds relevant document parts and generates answers")
    print("  - Use for documentation, knowledge bases, and wikis")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  Error: {e}")
        import traceback
        traceback.print_exc()
