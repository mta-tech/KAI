# Business Glossary Services

The Business Glossary Services module manages predefined SQL queries associated with specific business terms or jargon. By storing these definitions, KAI can intelligently query and handle specific business terms, enhancing its ability to process and understand business-related queries.

**Key Components**

1. **Imports**
   * **`HTTPException`**: Manages exceptions related to HTTP requests.
   * **`BusinessGlossaryRequest` & `UpdateBusinessGlossaryRequest`**: Models for handling incoming requests to create or update business glossaries.
   * **`BusinessGlossary`**: The model representing a business glossary entity.
   * **`BusinessGlossaryRepository`**: Repository for interacting with the business glossary database.
   * **`DatabaseConnectionRepository`**: Repository for managing database connections.
2.  **`BusinessGlossaryService` Class**

    The `BusinessGlossaryService` class encapsulates the business logic for managing business glossaries. It interacts with the `BusinessGlossaryRepository` to perform CRUD operations and validate database connections.

    **Initialization**

    * **`__init__(self, storage)`**: Initializes the service with a storage object, typically a database connection, and sets up the `BusinessGlossaryRepository`.

    **Methods**

    * **`get_business_glossaries(self, db_connection_id) -> list[BusinessGlossary]`**
      * Retrieves all business glossaries associated with a specific database connection.
      * Filters glossaries by the `db_connection_id`.
    * **`create_business_glossary(self, db_connection_id: str, business_glossary_request: BusinessGlossaryRequest) -> BusinessGlossary`**
      * Creates a new business glossary entry based on the provided request data.
      * Validates the existence of the associated database connection.
      * Returns the newly created `BusinessGlossary` object.
    * **`get_business_glossary(self, business_glossary_id) -> BusinessGlossary`**
      * Retrieves a business glossary by its ID.
      * Raises an `HTTPException` if the business glossary is not found.
    * **`update_business_glossary(self, business_glossary_id, request: UpdateBusinessGlossaryRequest) -> BusinessGlossary`**
      * Updates an existing business glossary with new data.
      * Applies changes only to the fields provided in the `UpdateBusinessGlossaryRequest`.
      * Returns the updated `BusinessGlossary` object.
    * **`delete_business_glossary(self, business_glossary_id) -> dict`**
      * Deletes a business glossary by its ID.
      * Verifies the existence of the business glossary before deletion.
      * Returns a success status if the deletion is successful.

**Usage Scenarios**

* **Creating Business Glossaries:** The `create_business_glossary` method allows users to define new business metrics, aliases, and SQL queries, linking them to specific database connections.
* **Retrieving Glossaries:** Use `get_business_glossaries` or `get_business_glossary` to access stored business glossary entries, facilitating the organization and retrieval of business-related definitions.
* **Updating Glossaries:** The `update_business_glossary` method enables users to modify existing glossary entries, ensuring they remain accurate and up-to-date.
* **Deleting Glossaries:** The `delete_business_glossary` method allows for the removal of glossary entries that are no longer needed, maintaining a clean and relevant glossary database.
