# Prompt Services

The Prompt Service is designed to manage historical prompts used in KAI. It facilitates the creation, retrieval, updating, and management of prompts associated with specific database connections.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages HTTP-related exceptions.
   * **`PromptRequest` & `UpdateMetadataRequest`**: Request models for creating and updating prompts.
   * **`DatabaseConnectionRepository`**: Manages database connections.
   * **`Prompt`**: Represents a prompt entity.
   * **`PromptRepository`**: Handles interactions with the prompt database.
2.  **`PromptService` Class**

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object for database operations and sets up the `PromptRepository`.

    **Methods**

    * **`create_prompt(self, prompt_request: PromptRequest) -> Prompt`**
      * Creates a new prompt based on the provided request data.
      * Validates the associated database connection and checks schema support.
      * Stores the new prompt in the database.
      * Returns the created `Prompt` object.
    * **`get_prompts(self, db_connection_id) -> list[Prompt]`**
      * Retrieves all prompts associated with a specific database connection.
      * Validates the database connection and returns a list of `Prompt` objects.
    * **`update_prompt(self, prompt_id, metadata_request: UpdateMetadataRequest) -> Prompt`**
      * Updates an existing prompt's metadata.
      * Raises an `HTTPException` if the prompt is not found.
      * Returns the updated `Prompt` object.
    * **`get_prompt(self, prompt_id) -> Prompt`**
      * Retrieves a specific prompt by its ID.
      * Raises an `HTTPException` if the prompt is not found.
      * Returns the requested `Prompt` object.

**Usage Scenarios**

* **Creating Prompts:** Define new prompts with associated text, metadata, and database connection details using `create_prompt`.
* **Retrieving Prompts:** Access all prompts related to a specific database connection or retrieve individual prompts by ID with `get_prompts` and `get_prompt`.
* **Updating Prompts:** Modify prompt metadata as needed using `update_prompt`.
* **Managing Prompts:** Handle the lifecycle of prompts, ensuring they are correctly stored and managed within the system.
