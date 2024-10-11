# Instruction API

The Instruction API allows you to manage instructions that guide SQL query generation based on conditions and rules. This API provides endpoints for creating, retrieving, updating, and deleting instructions.

### Endpoints

#### 1. Create an Instruction

**Endpoint:** `/api/v1/instructions`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new instruction with the specified database connection ID, condition, rules, default status, and optional metadata.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Retrieve All Instructions

**Endpoint:** `/api/v1/instructions`\
**Method:** `GET`\
**Description:** Retrieves a list of all instructions.

**Response:**

```json
[
    {
        "id": "string",
        "db_connection_id": "string",
        "condition": "string",
        "rules": "string",
        "is_default": boolean,
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific Instruction

**Endpoint:** `/api/v1/instructions/{instruction_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific instruction identified by `instruction_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. Update an Instruction

**Endpoint:** `/api/v1/instructions/{instruction_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing instruction identified by `instruction_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 5. Delete an Instruction

**Endpoint:** `/api/v1/instructions/{instruction_id}`\
**Method:** `DELETE`\
**Description:** Deletes a specific instruction identified by `instruction_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "condition": "string",
    "rules": "string",
    "is_default": boolean,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating an Instruction

To create a new instruction, send a `POST` request to `/api/v1/instructions`:

**Request:**

```http
POST /api/v1/instructions
Content-Type: application/json

{
    "db_connection_id": "db123",
    "condition": "If the sales amount is above 1000",
    "rules": "SELECT * FROM sales WHERE amount > 1000",
    "is_default": true,
    "metadata": {"created_by": "admin"}
}
```

**Response:**

```json
{
    "id": "instr123",
    "db_connection_id": "db123",
    "condition": "If the sales amount is above 1000",
    "rules": "SELECT * FROM sales WHERE amount > 1000",
    "is_default": true,
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving All Instructions

To retrieve a list of all instructions, send a `GET` request to `/api/v1/instructions`:

**Request:**

```http
GET /api/v1/instructions
```

**Response:**

```json
[
    {
        "id": "instr123",
        "db_connection_id": "db123",
        "condition": "If the sales amount is above 1000",
        "rules": "SELECT * FROM sales WHERE amount > 1000",
        "is_default": true,
        "metadata": {"created_by": "admin"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Retrieving a Specific Instruction

To retrieve a specific instruction, send a `GET` request to `/api/v1/instructions/{instruction_id}`:

**Request:**

```http
GET /api/v1/instructions/instr123
```

**Response:**

```json
{
    "id": "instr123",
    "db_connection_id": "db123",
    "condition": "If the sales amount is above 1000",
    "rules": "SELECT * FROM sales WHERE amount > 1000",
    "is_default": true,
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Updating an Instruction

To update an instruction, send a `PUT` request to `/api/v1/instructions/{instruction_id}`:

**Request:**

```http
PUT /api/v1/instructions/instr123
Content-Type: application/json

{
    "condition": "If the sales amount is above 5000",
    "rules": "SELECT * FROM sales WHERE amount > 5000",
    "is_default": false,
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "instr123",
    "db_connection_id": "db123",
    "condition": "If the sales amount is above 5000",
    "rules": "SELECT * FROM sales WHERE amount > 5000",
    "is_default": false,
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Deleting an Instruction

To delete an instruction, send a `DELETE` request to `/api/v1/instructions/{instruction_id}`:

**Request:**

```http
DELETE /api/v1/instructions/instr123
```

**Response:**

```json
{
    "id": "instr123",
    "db_connection_id": "db123",
    "condition": "If the sales amount is above 5000",
    "rules": "SELECT * FROM sales WHERE amount > 5000",
    "is_default": false,
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```
