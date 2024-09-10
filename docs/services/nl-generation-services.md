# NL Generation Services

The NL Generation Service Module handles natural language (NL) generation tasks in KAI, converting SQL queries into human-readable text. This module integrates with SQL and prompt services to provide comprehensive functionality for generating and managing NL outputs.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages HTTP-related exceptions.
   * **`NLGenerationRequest`, `NLGenerationsSQLGenerationRequest`, `PromptSQLGenerationNLGenerationRequest`**: Request models for various NL generation operations.
   * **`LLMConfig`, `NLGeneration`**: Models for NL generation and configuration.
   * **`NLGenerationRepository`**: Handles NL generation data storage and retrieval.
   * **`Prompt`**: Represents prompt data.
   * **`PromptService`**: Manages prompts.
   * **`SQLGeneration`, `SQLGenerationRepository`, `SQLGenerationService`**: Models and services for SQL generation.
   * **`GeneratesNlAnswer`**: Utility for generating NL answers from SQL.
2.  **`NLGenerationService` Class**

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object and sets up the `NLGenerationRepository`.

    **Methods**

    * **`create_nl_generation(self, sql_generation_id: str, nl_generation_request: NLGenerationRequest) -> NLGeneration`**
      * Creates a new NL generation entry linked to a specific SQL generation.
      * Uses the `GeneratesNlAnswer` utility to generate NL text.
      * Returns the created `NLGeneration` object.
    * **`create_sql_and_nl_generation(self, prompt_id: str, nl_generation_sql_generation_request: NLGenerationsSQLGenerationRequest) -> NLGeneration`**
      * Creates a SQL generation based on the prompt ID.
      * Subsequently creates an NL generation based on the newly created SQL generation.
      * Returns the created `NLGeneration` object.
    * **`create_prompt_sql_and_nl_generation(self, request: PromptSQLGenerationNLGenerationRequest) -> NLGeneration`**
      * Creates a new prompt.
      * Generates SQL based on the prompt.
      * Creates an NL generation based on the generated SQL.
      * Returns the created `NLGeneration` object.
    * **`get_nl_generations(self, sql_generation_id: str) -> list[NLGeneration]`**
      * Retrieves all NL generations associated with a specific SQL generation.
      * Returns a list of `NLGeneration` objects.
    * **`update_nl_generation(self, nl_generation_id, metadata_request) -> NLGeneration`**
      * Updates metadata for an existing NL generation.
      * Returns the updated `NLGeneration` object.
    * **`get_nl_generation(self, nl_generation_id: str) -> NLGeneration`**
      * Retrieves a specific NL generation by its ID.
      * Returns the requested `NLGeneration` object.

**Usage Scenarios**

* **Creating NL Generations:** Generate NL text from SQL queries or prompts using `create_nl_generation`, `create_sql_and_nl_generation`, or `create_prompt_sql_and_nl_generation`.
* **Retrieving NL Generations:** Access all NL generations associated with a specific SQL generation or a particular NL generation by ID using `get_nl_generations` and `get_nl_generation`.
* **Updating NL Generations:** Modify metadata of existing NL generations using `update_nl_generation`.
