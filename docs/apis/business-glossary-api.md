# Business Glossary API

The Business Glossary API provides endpoints for managing and interacting with business glossaries in your system. This includes creating, retrieving, updating, and deleting glossary entries. Below is a detailed guide on how to use these endpoints effectively.

### Endpoints

#### 1. Create a Business Glossary

**Endpoint:** `/api/v1/business_glossaries`\
**Method:** `POST`\
**Request Body:**

```json
{
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new business glossary entry with the specified metric, SQL definition, and optional aliases and metadata.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Retrieve Business Glossaries

**Endpoint:** `/api/v1/business_glossaries`\
**Method:** `GET`\
**Request Parameters:**

* `db_connection_id`: (Optional) The ID of the database connection to filter by.

**Description:** Retrieves a list of business glossaries. Optionally filter the list by database connection ID.

**Response:**

```json
[
    {
        "id": "string",
        "db_connection_id": "string",
        "metric": "string",
        "alias": ["string"],
        "sql": "string",
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific Business Glossary

**Endpoint:** `/api/v1/business_glossaries/{business_glossary_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific business glossary entry identified by `business_glossary_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. Update a Business Glossary

**Endpoint:** `/api/v1/business_glossaries/{business_glossary_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing business glossary entry identified by `business_glossary_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 5. Delete a Business Glossary

**Endpoint:** `/api/v1/business_glossaries/{business_glossary_id}`\
**Method:** `DELETE`\
**Description:** Deletes a specific business glossary entry identified by `business_glossary_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "metric": "string",
    "alias": ["string"],
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating a Business Glossary

To create a new business glossary, send a `POST` request to `/api/v1/business_glossaries`:

**Request:**

```http
POST /api/v1/business_glossaries
Content-Type: application/json

{
    "metric": "Revenue",
    "alias": ["Rev"],
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"}
}
```

**Response:**

```json
{
    "id": "abc123",
    "db_connection_id": "db123",
    "metric": "Revenue",
    "alias": ["Rev"],
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving Business Glossaries

To retrieve a list of business glossaries, send a `GET` request to `/api/v1/business_glossaries`:

**Request:**

```http
GET /api/v1/business_glossaries?db_connection_id=db123
```

**Response:**

```json
[
    {
        "id": "abc123",
        "db_connection_id": "db123",
        "metric": "Revenue",
        "alias": ["Rev"],
        "sql": "SELECT SUM(amount) AS revenue FROM sales",
        "metadata": {"created_by": "admin"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Retrieving a Specific Business Glossary

To retrieve a specific business glossary, send a `GET` request to `/api/v1/business_glossaries/{business_glossary_id}`:

**Request:**

```http
GET /api/v1/business_glossaries/abc123
```

**Response:**

```json
{
    "id": "abc123",
    "db_connection_id": "db123",
    "metric": "Revenue",
    "alias": ["Rev"],
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Updating a Business Glossary

To update a business glossary, send a `PUT` request to `/api/v1/business_glossaries/{business_glossary_id}`:

**Request:**

```http
PUT /api/v1/business_glossaries/abc123
Content-Type: application/json

{
    "metric": "Total Revenue",
    "alias": ["Total Rev"],
    "sql": "SELECT SUM(amount) AS total_revenue FROM sales",
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "abc123",
    "db_connection_id": "db123",
    "metric": "Total Revenue",
    "alias": ["Total Rev"],
    "sql": "SELECT SUM(amount) AS total_revenue FROM sales",
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Deleting a Business Glossary

To delete a business glossary, send a `DELETE` request to `/api/v1/business_glossaries/{business_glossary_id}`:

**Request:**

```http
DELETE /api/v1/business_glossaries/abc123
```

**Response:**

```json
{
    "id": "abc123",
    "db_connection_id": "db123",
    "metric": "Total Revenue",
    "alias": ["Total Rev"],
    "sql": "SELECT SUM(amount) AS total_revenue FROM sales",
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```
