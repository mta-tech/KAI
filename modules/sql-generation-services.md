# SQL Generation Services

The SQL Generation Service Module is responsible for generating SQL queries from prompts and managing their lifecycle within the KAI system. This module handles the creation, retrieval, updating, and execution of SQL queries and integrates with other services to provide comprehensive SQL generation capabilities.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages HTTP-related exceptions.
   * **`PromptSQLGenerationRequest`, `SQLGenerationRequest`, `UpdateMetadataRequest`**: Request models for SQL generation operations.
   * **`LLMConfig`, `SQLGeneration`**: Models for SQL generation and configuration.
   * **`SQLGenerationRepository`**: Handles SQL generation data storage and retrieval.
   * **`ContextStoreService`**: Manages context-related data.
   * **`PromptRepository`, `PromptService`**: Manages prompts.
   * **`SQLDatabase`**: Provides SQL database interactions.
   * **`SimpleEvaluator`**: Evaluates SQL queries.
   * **`SQLAgent`**: Generates SQL queries using language models.
   * **`create_sql_query_status`**: Updates SQL query status.
2.  **`SQLGenerationService` Class**

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object and sets up the `SQLGenerationRepository`.

    **Methods**

    * **`create_sql_generation(self, prompt_id: str, sql_generation_request: SQLGenerationRequest) -> SQLGeneration`**
      * Creates a new SQL generation entry linked to a specific prompt.
      * Handles SQL generation either from a provided SQL or by generating it via `SQLAgent`.
      * Evaluates the SQL query if required.
      * Returns the created `SQLGeneration` object.
    * **`create_prompt_and_sql_generation(self, prompt_sql_generation_request: PromptSQLGenerationRequest) -> SQLGeneration`**
      * Creates a new prompt.
      * Generates SQL based on the prompt.
      * Returns the created `SQLGeneration` object.
    * **`get_sql_generations(self, prompt_id: str) -> list[SQLGeneration]`**
      * Retrieves all SQL generations associated with a specific prompt.
      * Returns a list of `SQLGeneration` objects.
    * **`get_sql_generation(self, sql_generation_id: str) -> SQLGeneration`**
      * Retrieves a specific SQL generation by its ID.
      * Returns the requested `SQLGeneration` object.
    * **`update_sql_generation(self, sql_generation_id: str, metadata_request: UpdateMetadataRequest) -> SQLGeneration`**
      * Updates metadata for an existing SQL generation.
      * Returns the updated `SQLGeneration` object.
    * **`execute_sql_query(self, sql_generation_id: str, max_rows: int = 100) -> tuple[str, dict]`**
      * Executes the SQL query associated with a specific SQL generation.
      * Returns the result of the query execution.

    **Helpers**

    * **`generate_response_with_timeout(self, sql_generator: SQLAgent, user_prompt, db_connection, metadata=None)`**
      * Generates an SQL response with a timeout using `SQLAgent`.
    * **`update_error(self, sql_generation: SQLGeneration, error: str) -> SQLGeneration`**
      * Updates the error information for a SQL generation entry.
    * **`update_the_initial_sql_generation(self, initial_sql_generation: SQLGeneration, sql_generation: SQLGeneration)`**
      * Updates the initial SQL generation entry with details from the generated SQL.

**Usage Scenarios**

* **Creating SQL Generations:** Generate SQL queries based on prompts using `create_sql_generation` or `create_prompt_and_sql_generation`.
* **Retrieving SQL Generations:** Access all SQL generations associated with a specific prompt or a particular SQL generation by ID using `get_sql_generations` and `get_sql_generation`.
* **Updating SQL Generations:** Modify metadata of existing SQL generations using `update_sql_generation`.
* **Executing SQL Queries:** Run SQL queries associated with a SQL generation and get the results using `execute_sql_query`.
