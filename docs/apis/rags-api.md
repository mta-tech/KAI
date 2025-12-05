# RAGs API

The RAGs (Retrieval-Augmented Generation) API provides endpoints for managing documents and embeddings used for knowledge retrieval. This API allows you to upload documents, create text documents, manage document storage, create embeddings, and query the knowledge base.

### Endpoints

#### 1. Upload Document (PDF)

**Endpoint:** `/api/v1/rags/upload-document`\
**Method:** `POST`\
**Content-Type:** `multipart/form-data`\
**Request Body:**

- `file`: PDF file to upload

**Description:** Uploads a PDF document, extracts its text content, and stores it in the document store.

**Response:**

```json
{
    "id": "string",
    "title": "string",
    "content_type": "string",
    "document_size": 12345,
    "text_content": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Create Document (Text)

**Endpoint:** `/api/v1/rags/create-document`\
**Method:** `POST`\
**Request Body:**

```json
{
    "title": "string",
    "text_content": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new text document in the document store.

**Response:**

```json
{
    "id": "string",
    "title": "string",
    "content_type": "text",
    "document_size": 12345,
    "text_content": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 3. List All Documents

**Endpoint:** `/api/v1/rags/documents`\
**Method:** `GET`\
**Description:** Retrieves a list of all stored documents.

**Response:**

```json
[
    {
        "id": "string",
        "title": "string",
        "content_type": "string",
        "document_size": 12345,
        "text_content": "string",
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 4. Get Document by ID

**Endpoint:** `/api/v1/rags/documents/{document_id}`\
**Method:** `GET`\
**Description:** Retrieves a specific document by its ID.

**Response:**

```json
{
    "id": "string",
    "title": "string",
    "content_type": "string",
    "document_size": 12345,
    "text_content": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 5. Delete Document

**Endpoint:** `/api/v1/rags/documents/{document_id}`\
**Method:** `DELETE`\
**Description:** Deletes a specific document from the document store.

**Response:**

```json
{
    "message": "Document {document_id} successfully deleted"
}
```

#### 6. Create Embedding

**Endpoint:** `/api/v1/rags/embeddings/`\
**Method:** `POST`\
**Request Parameters:**

- `document_id`: (Required) The ID of the document to embed.

**Description:** Creates vector embeddings for a document and stores them in the vector store for later retrieval.

**Response:**

```json
{
    "message": "Document Embedded successfully"
}
```

#### 7. Query Knowledge Base

**Endpoint:** `/api/v1/rags/embeddings/`\
**Method:** `GET`\
**Request Parameters:**

- `query`: (Required) The natural language query to search the knowledge base.

**Description:** Queries the knowledge base using semantic search and returns an AI-generated answer based on the retrieved context.

**Response:**

```json
{
    "Final Answer": "string",
    "input_tokens_used": 123,
    "output_tokens_used": 456
}
```

### Example Usage

#### Uploading a PDF Document

To upload a PDF document, send a `POST` request to `/api/v1/rags/upload-document`:

**Request:**

```http
POST /api/v1/rags/upload-document
Content-Type: multipart/form-data

file: [PDF file binary]
```

**Response:**

```json
{
    "id": "doc123",
    "title": "annual_report.pdf",
    "content_type": "application/pdf",
    "document_size": 102400,
    "text_content": "Annual Report 2024...",
    "metadata": null,
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Creating a Text Document

To create a text document, send a `POST` request to `/api/v1/rags/create-document`:

**Request:**

```http
POST /api/v1/rags/create-document
Content-Type: application/json

{
    "title": "Company Policies",
    "text_content": "Our company policies include...",
    "metadata": {"category": "policies", "version": "1.0"}
}
```

**Response:**

```json
{
    "id": "doc456",
    "title": "Company Policies",
    "content_type": "text",
    "document_size": 1024,
    "text_content": "Our company policies include...",
    "metadata": {"category": "policies", "version": "1.0"},
    "created_at": "2024-09-09T12:35:00Z"
}
```

#### Creating an Embedding

To create an embedding for a document, send a `POST` request to `/api/v1/rags/embeddings/`:

**Request:**

```http
POST /api/v1/rags/embeddings/?document_id=doc456
```

**Response:**

```json
{
    "message": "Document Embedded successfully"
}
```

#### Querying the Knowledge Base

To query the knowledge base, send a `GET` request to `/api/v1/rags/embeddings/`:

**Request:**

```http
GET /api/v1/rags/embeddings/?query=What%20are%20the%20company%20vacation%20policies
```

**Response:**

```json
{
    "Final Answer": "Based on the company policies document, employees are entitled to 20 days of paid vacation per year...",
    "input_tokens_used": 150,
    "output_tokens_used": 75
}
```

### Error Handling

- **404 Not Found:** The specified document ID does not exist.
- **500 Internal Server Error:** An error occurred while processing the document or query.
