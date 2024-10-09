# Instruction Services

The Instruction Service Module in KAI is responsible for managing instructions that guide the LLM (Large Language Model) in generating SQL queries. Instructions store specific conditions and rules which help tailor the queries to meet specific requirements or handle particular scenarios.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages exceptions related to HTTP requests.
   * **`InstructionRequest` & `UpdateInstructionRequest`**: Models for handling incoming requests to create or update instructions.
   * **`DatabaseConnectionRepository`**: Repository for managing database connections.
   * **`Instruction`**: Model representing an instruction entity.
   * **`InstructionRepository`**: Repository for interacting with the instruction database.
2.  **`InstructionService` Class**

    The `InstructionService` class encapsulates the business logic for managing instructions. It validates database connections, manages instruction data, and handles embedding for conditions.

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object for database operations and sets up the `InstructionRepository`.

    **Methods**

    * **`create_instruction(self, instruction_request: InstructionRequest) -> Instruction`**
      * Creates a new instruction based on the provided request data.
      * Validates the existence of the associated database connection.
      * Computes an embedding for the instruction condition and stores the instruction in the database.
      * Returns the newly created `Instruction` object.
    * **`get_instruction(self, instruction_id) -> Instruction`**
      * Retrieves an instruction by its ID.
      * Raises an `HTTPException` if the instruction is not found.
    * **`get_instructions(self, db_connection_id) -> list[Instruction]`**
      * Retrieves all instructions associated with a specific database connection.
      * Returns a list of `Instruction` objects.
    * **`update_instruction(self, instruction_id, update_request: UpdateInstructionRequest) -> Instruction`**
      * Updates an existing instruction with new data from the update request.
      * Computes a new embedding for the condition if it is updated.
      * Returns the updated `Instruction` object.
    * **`delete_instruction(self, instruction_id) -> bool`**
      * Deletes an instruction by its ID.
      * Raises an `HTTPException` if the instruction is not found or if deletion fails.
      * Returns `True` if the instruction was successfully deleted.
    * **`get_embedding(self, text) -> list[float] | None`**
      * Placeholder method for computing embeddings for text.

**Usage Scenarios**

* **Creating Instructions:** The `create_instruction` method allows users to define new instructions, including conditions and rules, with support for embedding the condition text.
* **Retrieving Instructions:** Use `get_instruction` or `get_instructions` to access specific or all instructions associated with a database connection.
* **Updating Instructions:** The `update_instruction` method enables modification of existing instructions, including updating the condition and recalculating its embedding.
* **Deleting Instructions:** The `delete_instruction` method removes instructions from the system, ensuring that outdated or unnecessary instructions are cleaned up.
