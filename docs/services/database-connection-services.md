# Database Connection Services

The Database Connection Services module is designed to manage connections to various databases, enabling KAI (Knowledge Agent for Intelligence Query) to interact with and query data from multiple sources. This module handles the creation, listing, and configuration of database connections, and integrates with SQL databases to retrieve schema and table information.

**Key Components**

1. **Imports**
   * **`re`**: For regular expression operations.
   * **`DatabaseConnectionRequest`**: Request model for creating or updating database connections.
   * **`Storage`**: Represents the storage layer for database operations.
   * **`DatabaseConnection`**: Model representing a database connection entity.
   * **`DatabaseConnectionRepository`**: Repository for interacting with the database connection database.
   * **`TableDescriptionRepository`**: Repository for managing table descriptions.
   * **`FernetEncrypt`**: Utility for encrypting and decrypting sensitive information.
   * **`SQLDatabase`**: Provides SQL engine functionality for interacting with databases.
2.  **`DatabaseConnectionService` Class**

    The `DatabaseConnectionService` class encapsulates the logic for managing database connections. It integrates with SQL databases to handle schema and table management, and ensures secure handling of connection URIs.

    **Initialization**

    * **`__init__(self, scanner, storage: Storage)`**: Initializes the service with a scanner for table descriptions and a storage object for database operations.

    **Methods**

    * **`create_database_connection(self, request: DatabaseConnectionRequest) -> DatabaseConnection`**
      * Creates a new database connection based on the provided request data.
      * Encrypts the connection URI and retrieves schema and table information.
      * Stores the connection in the database and updates table descriptions.
      * Returns the newly created `DatabaseConnection` object.
    * **`list_database_connections(self) -> list[DatabaseConnection]`**
      * Retrieves and lists all existing database connections.
      * Returns a list of `DatabaseConnection` objects.
    * **`update_database_connection(self, db_connection_id: str, database_connection_request: DatabaseConnectionRequest) -> DatabaseConnection`**
      * Currently not implemented, intended for updating existing database connections.
    * **`remove_schema_in_uri(self, connection_uri: str, dialect: str) -> str`**
      * Removes schema-related parameters from the connection URI based on the database dialect.
      * Returns the updated URI.
    * **`add_schema_in_uri(self, connection_uri: str, schema: str, dialect: str) -> str`**
      * Adds schema parameters to the connection URI based on the database dialect.
      * Returns the updated URI.
    * **`get_sql_database(self, database_connection: DatabaseConnection, schema: str = None) -> SQLDatabase`**
      * Retrieves the SQL engine for a given database connection.
      * Optionally updates the connection URI with a specified schema.
      * Returns an instance of `SQLDatabase`.

**Usage Scenarios**

* **Creating Database Connections:** The `create_database_connection` method establishes a new connection to a database, encrypts the connection URI, and initializes schema and table information.
* **Listing Connections:** Use `list_database_connections` to retrieve and view all database connections stored in the system.
* **Managing Connection URIs:** Methods like `remove_schema_in_uri` and `add_schema_in_uri` facilitate the management of connection URIs, particularly for adjusting schema parameters.
* **Retrieving SQL Engine:** The `get_sql_database` method provides access to the SQL engine for executing queries and managing database interactions.
