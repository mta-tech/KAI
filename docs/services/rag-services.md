# RAG Services

The RAG (Retrieval-Augmented Generation) Services module provides document management and knowledge retrieval capabilities in KAI. This module handles document storage, embedding generation, and semantic search for answering natural language queries using stored knowledge.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages HTTP-related exceptions.
   * **`TextRequest`, `EmbeddingRequest`**: Request models for document and embedding operations.
   * **`DocumentStore`, `RetrieveKnowledge`**: Models representing documents and query responses.
   * **`DocumentRepository`**: Repository for document storage and retrieval.
   * **`LlamaIndex Components`**: Integration with LlamaIndex for document processing and retrieval.
   * **`TypesenseVectorStore`**: Vector store for storing and querying embeddings.

2. **`DocumentService` Class**

   The `DocumentService` class manages document storage operations including creation, retrieval, and deletion.

   **Initialization**

   * **`__init__(self, storage: Storage)`**: Initializes the service with a storage object and sets up the `DocumentRepository`.

   **Methods**

   * **`create_document(self, embedding_request: TextRequest) -> DocumentStore`**
     * Creates a new document entry with the provided text content and metadata.
     * Returns the created `DocumentStore` object.
   * **`get_document(self, document_id) -> DocumentStore`**
     * Retrieves a document by its ID.
     * Raises an `HTTPException` if the document is not found.
   * **`get_documents(self) -> list[DocumentStore]`**
     * Retrieves all documents from the document store.
     * Returns a list of `DocumentStore` objects.
   * **`delete_document(self, document_id) -> bool`**
     * Deletes a document by its ID.
     * Raises an `HTTPException` if the document is not found or deletion fails.
     * Returns `True` if successful.

3. **`EmbeddingService` Class**

   The `EmbeddingService` class handles embedding generation and knowledge retrieval using vector search.

   **Initialization**

   * **`__init__(self, storage: Storage)`**: Initializes the service with embedding model, vector store, and query engine configurations.

   **Methods**

   * **`create_embedding(self, embedding_request: EmbeddingRequest) -> bool`**
     * Creates vector embeddings for a document using the ingestion pipeline.
     * Processes the document through text splitting and embedding generation.
     * Returns `True` if successful.
   * **`create_ingestion_pipeline(self, vector_store: TypesenseVectorStore)`**
     * Creates a LlamaIndex ingestion pipeline with text splitting and embedding transformations.
     * Returns the configured `IngestionPipeline`.
   * **`create_llama_document(self, embedding_request: EmbeddingRequest) -> Document`**
     * Converts an embedding request into a LlamaIndex Document object.
     * Returns the `Document` with metadata.
   * **`create_query_engine(self, top_k: int = 4, cutoff: float = 0.80) -> RetrieverQueryEngine`**
     * Creates a query engine for semantic search with configurable top-k retrieval.
     * Returns the configured `RetrieverQueryEngine`.
   * **`query(self, query_request: str) -> RetrieveKnowledge`**
     * Executes a natural language query against the knowledge base.
     * Returns a `RetrieveKnowledge` object with the answer and token usage.

4. **`VectorDBRetriever` Class**

   A custom retriever class that extends LlamaIndex's `BaseRetriever` for vector store queries.

   **Methods**

   * **`_retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]`**
     * Retrieves relevant nodes from the vector store based on query embeddings.
     * Returns nodes with similarity scores.

**Usage Scenarios**

* **Storing Documents:** Use `DocumentService.create_document` to store text documents that can later be embedded and queried.
* **Generating Embeddings:** Use `EmbeddingService.create_embedding` to convert documents into vector embeddings stored in Typesense.
* **Knowledge Retrieval:** Use `EmbeddingService.query` to perform semantic search and get AI-generated answers based on stored knowledge.
* **Managing Documents:** Use `get_document`, `get_documents`, and `delete_document` to manage the document lifecycle.

**Architecture**

The RAG module uses a two-stage approach:
1. **Ingestion**: Documents are chunked, embedded, and stored in a Typesense vector store.
2. **Retrieval**: Queries are embedded, similar documents are retrieved, and an LLM generates answers based on the retrieved context.
