# Table Description Service

The **Table Description Service** in KAI provides detailed information about database schemas, enabling the SQL Generation module to understand the database structure and generate accurate SQL queries. This service includes a database scanning which scans database schemas and marks tables that have been scanned.

**Key Components**

1. **Imports**
   * **`BackgroundTasks`**: Manages background tasks for asynchronous operations.
   * **`HTTPException`**: Manages HTTP-related exceptions.
   * **`ScannerRequest`, `TableDescriptionRequest`**: Request models for scanning and updating table descriptions.
   * **`TableDescription`**: Response model for table descriptions.
   * **`Storage`**: Storage interface for database operations.
   * **`TableDescriptionRepository`**: Handles table description data storage and retrieval.
   * **`SqlAlchemyScanner`**: Scans and updates table descriptions.
   * **`DatabaseConnectionRepository`, `DatabaseConnectionService`**: Manages database connections and interactions.
2.  **`TableDescriptionService` Class**

    **Initialization**

    * **`__init__(self, storage: Storage)`**: Initializes the service with a storage object.

    **Methods**

    * **`scan_db(self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks) -> list[TableDescription]`**
      * Scans tables and columns based on provided `table_description_ids`.
      * Utilizes background tasks for asynchronous scanning.
      * Returns a list of `TableDescription` objects representing the scanned tables.
    * **`refresh_table_description(self, database_connection_id: str) -> list[TableDescription]`**
      * Refreshes the table descriptions for a given database connection.
      * Retrieves updated table and view information from the database.
      * Returns a list of updated `TableDescription` objects.
    * **`update_table_description(self, table_description_id: str, table_description_request: TableDescriptionRequest) -> TableDescription`**
      * Updates the details of a specific table description.
      * Returns the updated `TableDescription` object.
      * Raises an exception if the table description is not found or the update fails.
    * **`get_table_description(self, table_description_id: str) -> TableDescription`**
      * Retrieves a specific table description by its ID.
      * Returns the `TableDescription` object.
      * Raises an exception if the table description is not found.
    * **`list_table_descriptions(self, db_connection_id: str, table_name: str | None = None) -> list[TableDescription]`**
      * Lists table descriptions for a given database connection ID and optional table name.
      * Returns a list of `TableDescription` objects.

    **Helpers**

    * **`async_scanning(scanner: SqlAlchemyScanner, engine, table_descriptions, storage)`**
      * Asynchronously scans and updates table descriptions using `SqlAlchemyScanner`.
      * Runs in the background to improve performance.

**Usage Scenarios**

* **Scanning Databases**: Use `scan_db` to scan and update table structures based on given table descriptions.
* **Refreshing Table Descriptions**: Use `refresh_table_description` to get updated details for tables in a specific database connection.
* **Updating Table Metadata**: Use `update_table_description` to modify metadata for a specific table.
* **Retrieving and Listing Table Descriptions**: Use `get_table_description` to fetch details for a specific table and `list_table_descriptions` to list tables for a given database connection.
