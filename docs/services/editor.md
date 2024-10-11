# Context Store Services

The Context Store Services module is integral to the KAI (Knowledge Agent for Intelligence Query) system. It manages the storage of historical prompts and their corresponding SQL queries. By saving this data, the module allows KAI to bypass calling the LLM (Large Language Model) when a similar prompt has already been processed. This approach reduces operational costs and significantly improves response times by leveraging previously generated results.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Handles errors and exceptions related to HTTP requests.
   * **`ContextStoreRequest` & `UpdateContextStoreRequest`**: Request models for creating and updating context stores.
   * **`ContextStore`**: The model representing a context store entity.
   * **`ContextStoreRepository`**: Repository for interacting with the context store database.
   * **`DatabaseConnectionRepository`**: Repository for handling database connections.
2.  **`ContextStoreService` Class**

    The `ContextStoreService` class encapsulates the core functionality for managing context stores. It interacts with the repositories to perform CRUD operations and other specialized tasks like full-text search.

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object, typically a database connection, and sets up the `ContextStoreRepository`.

    **Methods**

    * **`create_context_store(self, context_store_request: ContextStoreRequest) -> ContextStore`**
      * Creates a new context store based on the provided request data.
      * Validates the existence of the associated database connection.
      * Returns the newly created `ContextStore` object.
    * **`get_context_store(self, context_store_id) -> ContextStore`**
      * Retrieves a context store by its ID.
      * Raises an `HTTPException` if the context store is not found.
    * **`get_context_stores(self, db_connection_id) -> list[ContextStore]`**
      * Retrieves all context stores associated with a specific database connection.
      * Filters context stores by the `db_connection_id`.
    * **`update_context_store(self, context_store_id, update_request: UpdateContextStoreRequest) -> ContextStore`**
      * Updates an existing context store with new data.
      * Applies changes only to the fields provided in the `UpdateContextStoreRequest`.
      * Returns the updated `ContextStore` object.
    * **`delete_context_store(self, context_store_id) -> bool`**
      * Deletes a context store by its ID.
      * Verifies the existence of the context store before deletion.
      * Returns `True` if the deletion is successful.
    * **`full_text_search(self, db_connection_id, prompt) -> ContextStore`**
      * Performs a full-text search for a context store based on the prompt and associated database connection ID.
      * Returns the matched `ContextStore` object.
    * **`create_embedding(self, context_store_id) -> ContextStore`**
      * Generates embeddings for prompts in the context store, allowing for more efficient retrieval and comparison of similar queries.



**Usage Scenarios**

* **Creating Context Stores:** The `create_context_store` method is used to create and store new prompts, SQL queries, and metadata linked to a specific database connection.
* **Retrieving Context Data:** Use `get_context_store` or `get_context_stores` to retrieve stored context based on ID or database connection.
* **Updating Context:** The `update_context_store` method allows for updating existing context stores with new data.
* **Deleting Context:** The `delete_context_store` method facilitates the removal of context stores that are no longer needed.
* **Full-Text Search:** The `full_text_search` method enables searching through context stores using prompts, allowing for quick retrieval of relevant data.
