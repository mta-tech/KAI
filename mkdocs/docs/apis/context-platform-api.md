# Context Platform API

The Context Platform API provides endpoints for managing reusable context assets with lifecycle management. Context assets are domain knowledge artifacts that can be versioned, tagged, and shared across missions and database connections.

## Asset Types

- **table_description**: Descriptive metadata about database tables
- **glossary**: Business terminology and definitions
- **instruction**: Domain-specific analysis instructions
- **skill**: Reusable analysis patterns and templates

## Lifecycle States

- **draft**: Initial creation, not yet verified
- **verified**: Validated by domain expert
- **published**: Approved for reuse across missions
- **deprecated**: Superseded or no longer relevant

## Lifecycle Transitions

```
draft -> verified    (after domain expert review)
verified -> published (after approval for reuse)
published -> deprecated (when superseded or obsolete)
Any state -> draft     (for revision cycles)
```

---

## Context Asset Endpoints

### 1. Create Context Asset

**Endpoint:** `/api/v1/context-assets`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "asset_type": "table_description | glossary | instruction | skill",
    "canonical_key": "string",
    "name": "string",
    "content": {},
    "content_text": "string",
    "description": "string",
    "author": "string",
    "tags": ["string"],
    "metadata": {}
}
```

**Description:** Creates a new context asset in DRAFT state. The asset is uniquely identified by the combination of `db_connection_id`, `asset_type`, `canonical_key`, and `version`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "draft",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### 2. List Context Assets

**Endpoint:** `/api/v1/context-assets`\
**Method:** `GET`\
**Request Parameters:**

- `db_connection_id`: (Required) The ID of the database connection
- `asset_type`: (Optional) Filter by asset type
- `lifecycle_state`: (Optional) Filter by lifecycle state (draft, verified, published, deprecated)
- `limit`: (Optional) Maximum number of results (default: 100)

**Description:** Retrieves a list of context assets with optional filtering.

**Response:**

```json
[
    {
        "id": "string",
        "db_connection_id": "string",
        "asset_type": "string",
        "canonical_key": "string",
        "version": "string",
        "name": "string",
        "description": "string",
        "content": {},
        "content_text": "string",
        "lifecycle_state": "string",
        "tags": ["string"],
        "author": "string",
        "parent_asset_id": "string",
        "created_at": "2024-09-09T12:34:56Z",
        "updated_at": "2024-09-09T12:34:56Z"
    }
]
```

### 3. Get Context Asset

**Endpoint:** `/api/v1/context-assets/{db_connection_id}/{asset_type}/{canonical_key}`\
**Method:** `GET`\
**Request Parameters:**

- `db_connection_id`: (Required) The database connection ID
- `asset_type`: (Required) The asset type
- `canonical_key`: (Required) The canonical key of the asset
- `version`: (Optional) Version string (default: "latest")

**Description:** Retrieves a specific context asset by key.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "string",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### 4. Update Context Asset

**Endpoint:** `/api/v1/context-assets/{asset_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "tags": ["string"]
}
```

**Description:** Updates an existing context asset. Only DRAFT assets can be updated.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "draft",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### 5. Delete Context Asset

**Endpoint:** `/api/v1/context-assets/{db_connection_id}/{asset_type}/{canonical_key}`\
**Method:** `DELETE`\
**Request Parameters:**

- `db_connection_id`: (Required) The database connection ID
- `asset_type`: (Required) The asset type
- `canonical_key`: (Required) The canonical key
- `version`: (Optional) Version to delete (default: latest)

**Description:** Deletes a context asset. Only DRAFT assets can be deleted.

**Response:**

```json
{
    "message": "Asset {asset_type}/{canonical_key} deleted successfully"
}
```

### 6. Search Context Assets

**Endpoint:** `/api/v1/context-assets/search`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "query": "string",
    "asset_type": "string",
    "limit": 10
}
```

**Description:** Searches context assets using semantic and keyword matching.

**Response:**

```json
[
    {
        "asset": {
            "id": "string",
            "db_connection_id": "string",
            "asset_type": "string",
            "canonical_key": "string",
            "version": "string",
            "name": "string",
            "description": "string",
            "content": {},
            "content_text": "string",
            "lifecycle_state": "string",
            "tags": ["string"],
            "author": "string",
            "parent_asset_id": "string",
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T12:34:56Z"
        },
        "score": 0.95,
        "match_type": "hybrid"
    }
]
```

---

## Lifecycle Management Endpoints

### 7. Promote Asset to Verified

**Endpoint:** `/api/v1/context-assets/{asset_id}/promote/verified`\
**Method:** `POST`\
**Request Body:**

```json
{
    "promoted_by": "string",
    "change_note": "string"
}
```

**Description:** Promotes an asset from DRAFT to VERIFIED state. Requires domain expert approval.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "verified",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z",
    "promoted_by": "string",
    "promoted_at": "2024-09-09T12:34:56Z",
    "change_note": "string"
}
```

### 8. Promote Asset to Published

**Endpoint:** `/api/v1/context-assets/{asset_id}/promote/published`\
**Method:** `POST`\
**Request Body:**

```json
{
    "promoted_by": "string",
    "change_note": "string"
}
```

**Description:** Promotes an asset from VERIFIED to PUBLISHED state. Requires final approval for reuse across missions.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "published",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z",
    "promoted_by": "string",
    "promoted_at": "2024-09-09T12:34:56Z",
    "change_note": "string"
}
```

### 9. Deprecate Asset

**Endpoint:** `/api/v1/context-assets/{asset_id}/deprecate`\
**Method:** `POST`\
**Request Body:**

```json
{
    "promoted_by": "string",
    "reason": "string"
}
```

**Description:** Deprecates a published asset.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "deprecated",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### 10. Create Draft Revision

**Endpoint:** `/api/v1/context-assets/{asset_id}/revision`\
**Method:** `POST`\
**Request Body:**

```json
{
    "author": "string"
}
```

**Description:** Creates a new DRAFT revision of an existing asset. This allows editing published assets by creating a new draft version.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "asset_type": "string",
    "canonical_key": "string",
    "version": "string",
    "name": "string",
    "description": "string",
    "content": {},
    "content_text": "string",
    "lifecycle_state": "draft",
    "tags": ["string"],
    "author": "string",
    "parent_asset_id": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### 11. Get Asset Version History

**Endpoint:** `/api/v1/context-assets/{asset_id}/versions`\
**Method:** `GET`\
**Description:** Retrieves the version history for an asset.

**Response:**

```json
[
    {
        "id": "string",
        "asset_id": "string",
        "version": "string",
        "name": "string",
        "description": "string",
        "content": {},
        "content_text": "string",
        "lifecycle_state": "string",
        "author": "string",
        "change_summary": "string",
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

### 12. Get Asset Tags

**Endpoint:** `/api/v1/context-assets/tags`\
**Method:** `GET`\
**Request Parameters:**

- `category`: (Optional) Filter tags by category

**Description:** Retrieves all context asset tags, optionally filtered by category.

**Response:**

```json
[
    {
        "id": "string",
        "name": "string",
        "category": "string",
        "description": "string",
        "usage_count": 5,
        "last_used_at": "2024-09-09T12:34:56Z",
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

---

## Example Usage

### Creating a Context Asset

To create a new context asset, send a `POST` request to `/api/v1/context-assets`:

**Request:**

```http
POST /api/v1/context-assets
Content-Type: application/json

{
    "db_connection_id": "db123",
    "asset_type": "glossary",
    "canonical_key": "monthly_active_users",
    "name": "Monthly Active Users",
    "content": {
        "definition": "Number of unique users who engaged with the platform at least once in a calendar month",
        "formula": "COUNT(DISTINCT user_id) WHERE activity_date >= month_start AND activity_date < month_end",
        "category": "user_metrics"
    },
    "content_text": "Monthly Active Users (MAU) - Number of unique users who engaged with the platform at least once in a calendar month",
    "description": "Key metric for tracking user engagement",
    "author": "data-team@example.com",
    "tags": ["metrics", "user-engagement", "kpi"]
}
```

**Response:**

```json
{
    "id": "asset_abc123",
    "db_connection_id": "db123",
    "asset_type": "glossary",
    "canonical_key": "monthly_active_users",
    "version": "1.0.0",
    "name": "Monthly Active Users",
    "description": "Key metric for tracking user engagement",
    "content": {
        "definition": "Number of unique users who engaged with the platform at least once in a calendar month",
        "formula": "COUNT(DISTINCT user_id) WHERE activity_date >= month_start AND activity_date < month_end",
        "category": "user_metrics"
    },
    "content_text": "Monthly Active Users (MAU) - Number of unique users who engaged with the platform at least once in a calendar month",
    "lifecycle_state": "draft",
    "tags": ["metrics", "user-engagement", "kpi"],
    "author": "data-team@example.com",
    "parent_asset_id": null,
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

### Promoting an Asset

To promote an asset from DRAFT to VERIFIED:

**Request:**

```http
POST /api/v1/context-assets/asset_abc123/promote/verified
Content-Type: application/json

{
    "promoted_by": "domain-expert@example.com",
    "change_note": "Reviewed definition and formula. Accurately represents MAU calculation."
}
```

**Response:**

```json
{
    "id": "asset_abc123",
    "db_connection_id": "db123",
    "asset_type": "glossary",
    "canonical_key": "monthly_active_users",
    "version": "1.0.0",
    "name": "Monthly Active Users",
    "description": "Key metric for tracking user engagement",
    "content": {
        "definition": "Number of unique users who engaged with the platform at least once in a calendar month",
        "formula": "COUNT(DISTINCT user_id) WHERE activity_date >= month_start AND activity_date < month_end",
        "category": "user_metrics",
        "promoted_by": "domain-expert@example.com",
        "promoted_at": "2024-09-09T14:00:00Z",
        "change_note": "Reviewed definition and formula. Accurately represents MAU calculation."
    },
    "content_text": "Monthly Active Users (MAU) - Number of unique users who engaged with the platform at least once in a calendar month",
    "lifecycle_state": "verified",
    "tags": ["metrics", "user-engagement", "kpi"],
    "author": "data-team@example.com",
    "parent_asset_id": null,
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T14:00:00Z",
    "promoted_by": "domain-expert@example.com",
    "promoted_at": "2024-09-09T14:00:00Z",
    "change_note": "Reviewed definition and formula. Accurately represents MAU calculation."
}
```

### Searching Context Assets

To search for context assets:

**Request:**

```http
POST /api/v1/context-assets/search
Content-Type: application/json

{
    "db_connection_id": "db123",
    "query": "user engagement metrics",
    "asset_type": "glossary",
    "limit": 5
}
```

**Response:**

```json
[
    {
        "asset": {
            "id": "asset_abc123",
            "db_connection_id": "db123",
            "asset_type": "glossary",
            "canonical_key": "monthly_active_users",
            "version": "1.0.0",
            "name": "Monthly Active Users",
            "description": "Key metric for tracking user engagement",
            "content": {
                "definition": "Number of unique users who engaged with the platform at least once in a calendar month",
                "formula": "COUNT(DISTINCT user_id) WHERE activity_date >= month_start AND activity_date < month_end",
                "category": "user_metrics"
            },
            "content_text": "Monthly Active Users (MAU) - Number of unique users who engaged with the platform at least once in a calendar month",
            "lifecycle_state": "verified",
            "tags": ["metrics", "user-engagement", "kpi"],
            "author": "data-team@example.com",
            "parent_asset_id": null,
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T14:00:00Z"
        },
        "score": 0.95,
        "match_type": "hybrid"
    }
]
```

### Python Examples

#### Creating a Context Asset

```python
import requests

url = "http://localhost:8015/api/v1/context-assets"
headers = {"Content-Type": "application/json"}

data = {
    "db_connection_id": "db123",
    "asset_type": "glossary",
    "canonical_key": "monthly_active_users",
    "name": "Monthly Active Users",
    "content": {
        "definition": "Number of unique users who engaged with the platform at least once in a calendar month",
        "formula": "COUNT(DISTINCT user_id) WHERE activity_date >= month_start AND activity_date < month_end",
        "category": "user_metrics"
    },
    "content_text": "Monthly Active Users (MAU) - Number of unique users who engaged with the platform at least once in a calendar month",
    "description": "Key metric for tracking user engagement",
    "author": "data-team@example.com",
    "tags": ["metrics", "user-engagement", "kpi"]
}

response = requests.post(url, json=data, headers=headers)
asset = response.json()
print(f"Created asset: {asset['id']} in {asset['lifecycle_state']} state")
```

#### Listing Context Assets

```python
import requests

url = "http://localhost:8015/api/v1/context-assets"
params = {
    "db_connection_id": "db123",
    "lifecycle_state": "published",
    "limit": 50
}

response = requests.get(url, params=params)
assets = response.json()
for asset in assets:
    print(f"{asset['name']} ({asset['asset_type']}) - {asset['lifecycle_state']}")
```

#### Promoting an Asset

```python
import requests

asset_id = "asset_abc123"
url = f"http://localhost:8015/api/v1/context-assets/{asset_id}/promote/verified"
headers = {"Content-Type": "application/json"}

data = {
    "promoted_by": "domain-expert@example.com",
    "change_note": "Reviewed and validated"
}

response = requests.post(url, json=data, headers=headers)
updated_asset = response.json()
print(f"Asset promoted to: {updated_asset['lifecycle_state']}")
```

---

## Error Handling

### Common Error Responses

**400 Bad Request**

- Invalid asset type
- Invalid lifecycle state
- Attempting to update/delete a non-DRAFT asset
- Invalid lifecycle transition

```json
{
    "detail": "Cannot update asset in 'verified' state. Only DRAFT assets can be updated."
}
```

**404 Not Found**

- Asset not found with specified key
- Version not found

```json
{
    "detail": "Asset not found: glossary/monthly_active_users@latest"
}
```

**500 Internal Server Error**

- Unexpected server error

```json
{
    "detail": "Internal server error message"
}
```

### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `400: Invalid asset type` | Asset type not one of: table_description, glossary, instruction, skill | Verify asset_type is valid |
| `400: Cannot update asset in 'verified' state` | Attempting to update non-DRAFT asset | Create a draft revision first |
| `400: Invalid lifecycle transition` | Attempting invalid state transition | Follow allowed lifecycle transitions |
| `404: Asset not found` | Asset with given key does not exist | Verify db_connection_id, asset_type, canonical_key are correct |
| `404: Version not found` | Specified version does not exist | Use 'latest' or verify version string |
