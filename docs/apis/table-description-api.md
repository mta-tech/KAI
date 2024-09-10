# Table Description API

The Table Description API allows you to manage and interact with table descriptions in your database. This includes endpoints to synchronize schemas, refresh table descriptions, update table descriptions, and retrieve table descriptions. Below is a guide on how to use these endpoints effectively.

### Endpoints

#### 1. Synchronize Database Schemas

**Endpoint:** `/api/v1/table-descriptions/sync-schemas`\
**Method:** `POST`\
**Request Body:**

```json
{
    "table_description_ids": ["string"],
    "metadata": {"key": "value"}
}
```

**Description:** Scans and synchronizes schemas based on the provided table description IDs. This endpoint updates table descriptions to reflect the current state of the database schema.

**Response:**

```json
[
    {
        "id": "string",
        "description": "string",
        "columns": [
            {
                "name": "string",
                "description": "string",
                "is_primary_key": true,
                "data_type": "string",
                "low_cardinality": true,
                "categories": ["string"],
                "foreign_key": {
                    "field_name": "string",
                    "reference_table": "string"
                }
            }
        ],
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 2. Refresh Table Descriptions

**Endpoint:** `/api/v1/table-descriptions/refresh`\
**Method:** `POST`\
**Request Body:**

```json
{
    "database_connection_id": "string"
}
```

**Description:** Refreshes the table descriptions for a given database connection ID. This updates the table descriptions based on the current schema of the specified database connection.

**Response:**

```json
[
    {
        "id": "string",
        "description": "string",
        "columns": [
            {
                "name": "string",
                "description": "string",
                "is_primary_key": true,
                "data_type": "string",
                "low_cardinality": true,
                "categories": ["string"],
                "foreign_key": {
                    "field_name": "string",
                    "reference_table": "string"
                }
            }
        ],
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Update a Table Description

**Endpoint:** `/api/v1/table-descriptions/{table_description_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "description": "string",
    "columns": [
        {
            "name": "string",
            "description": "string",
            "is_primary_key": true,
            "data_type": "string",
            "low_cardinality": true,
            "categories": ["string"],
            "foreign_key": {
                "field_name": "string",
                "reference_table": "string"
            }
        }
    ],
    "metadata": {"key": "value"}
}
```

**Description:** Updates the description and details of a specific table identified by `table_description_id`.

**Response:**

```json
{
    "id": "string",
    "description": "string",
    "columns": [
        {
            "name": "string",
            "description": "string",
            "is_primary_key": true,
            "data_type": "string",
            "low_cardinality": true,
            "categories": ["string"],
            "foreign_key": {
                "field_name": "string",
                "reference_table": "string"
            }
        }
    ],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. List Table Descriptions

**Endpoint:** `/api/v1/table-descriptions`\
**Method:** `GET`\
**Request Parameters:**

* `db_connection_id`: (Required) The ID of the database connection.
* `table_name`: (Optional) The name of the table to filter by.

**Description:** Retrieves a list of table descriptions for the specified database connection. Optionally, filter by table name.

**Response:**

```json
[
    {
        "id": "string",
        "description": "string",
        "columns": [
            {
                "name": "string",
                "description": "string",
                "is_primary_key": true,
                "data_type": "string",
                "low_cardinality": true,
                "categories": ["string"],
                "foreign_key": {
                    "field_name": "string",
                    "reference_table": "string"
                }
            }
        ],
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 5. Retrieve a Table Description

**Endpoint:** `/api/v1/table-descriptions/{table_description_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific table description identified by `table_description_id`.

**Response:**

```json
{
    "id": "string",
    "description": "string",
    "columns": [
        {
            "name": "string",
            "description": "string",
            "is_primary_key": true,
            "data_type": "string",
            "low_cardinality": true,
            "categories": ["string"],
            "foreign_key": {
                "field_name": "string",
                "reference_table": "string"
            }
        }
    ],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Synchronizing Database Schemas

To synchronize database schemas, send a `POST` request to `/api/v1/table-descriptions/sync-schemas`:

**Request:**

```http
POST /api/v1/table-descriptions/sync-schemas
Content-Type: application/json

{
    "table_description_ids": ["abc123", "def456"],
    "metadata": {"sync": "true"}
}
```

**Response:**

```json
[
    {
        "id": "abc123",
        "description": "Updated table description",
        "columns": [
            {
                "name": "column1",
                "description": "Primary column",
                "is_primary_key": true,
                "data_type": "INTEGER",
                "low_cardinality": false,
                "categories": ["int"],
                "foreign_key": null
            }
        ],
        "metadata": {"sync_status": "completed"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Refreshing Table Descriptions

To refresh table descriptions, send a `POST` request to `/api/v1/table-descriptions/refresh`:

**Request:**

```http
POST /api/v1/table-descriptions/refresh
Content-Type: application/json

{
    "database_connection_id": "db123"
}
```

**Response:**

```json
[
    {
        "id": "xyz789",
        "description": "Refreshed table description",
        "columns": [
            {
                "name": "columnA",
                "description": "Description of column A",
                "is_primary_key": false,
                "data_type": "VARCHAR",
                "low_cardinality": true,
                "categories": ["string"],
                "foreign_key": {
                    "field_name": "ref_column",
                    "reference_table": "reference_table"
                }
            }
        ],
        "metadata": {"refresh_status": "successful"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Updating a Table Description

To update a table description, send a `PUT` request to `/api/v1/table-descriptions/{table_description_id}`:

**Request:**

```http
PUT /api/v1/table-descriptions/xyz789
Content-Type: application/json

{
    "description": "New table description",
    "columns": [
        {
            "name": "columnB",
            "description": "Updated description",
            "is_primary_key": false,
            "data_type": "DATE",
            "low_cardinality": false,
            "categories": ["date"],
            "foreign_key": null
        }
    ],
    "metadata": {"update": "true"}
}
```

**Response:**

```json
{
    "id": "xyz789",
    "description": "New table description",
    "columns": [
        {
            "name": "columnB",
            "description": "Updated description",
            "is_primary_key": false,
            "data_type": "DATE",
            "low_cardinality": false,
            "categories": ["date"],
            "foreign_key": null
        }
    ],
    "metadata": {"update_status": "completed"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Listing Table Descriptions

To list table descriptions, send a `GET` request to `/api/v1/table-descriptions`:

**Request:**

```http
GET /api/v1/table-descriptions?db_connection_id=db123
```

**Response:**

```json
[
    {
        "id": "xyz789",
        "description": "Table description",
        "columns": [
            {
                "name": "columnB",
                "description": "Column description",
                "is_primary_key": false,
                "data_type": "DATE",
                "low_cardinality": false,
                "categories": ["date"],
                "foreign_key": null
            }
        ],
        "metadata": {"list_status": "successful"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```
