# Aliases API Documentation

API for managing aliases for tables and columns.

**Base URL:** `/api/v1/aliases`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create a new alias |
| GET | `/` | Get all aliases |
| GET | `/{alias_id}` | Get a specific alias |
| PUT | `/{alias_id}` | Update an alias |
| DELETE | `/{alias_id}` | Delete an alias |
| GET | `/get-by-name` | Get an alias by name |

---

## Data Types

### AliasRequest (Request)

```typescript
interface AliasRequest {
  db_connection_id: string;
  name: string;
  target_name: string;
  target_type: string;
  description?: string;
  metadata?: Record<string, any>;
}
```

### AliasResponse (Response)

```typescript
interface AliasResponse {
  id: string;
  db_connection_id: string;
  name: string;
  target_name: string;
  target_type: string;
  description?: string;
  metadata?: Record<string, any>;
  created_at: string;
}
```

### UpdateAliasRequest (Request)

```typescript
interface UpdateAliasRequest {
  name?: string;
  target_name?: string;
  target_type?: string;
  description?: string;
  metadata?: Record<string, any>;
}
```

---

## POST /

Create a new alias.

### Request Body

`AliasRequest`

### Response

`AliasResponse`

---

## GET /

Get all aliases.

### Query Parameters

- `db_connection_id` (string, required)
- `target_type` (string, optional)

### Response

`AliasResponse[]`

---

## GET /{alias_id}

Get a specific alias.

### Path Parameters

- `alias_id` (string, required)

### Response

`AliasResponse`

---

## PUT /{alias_id}

Update an alias.

### Path Parameters

- `alias_id` (string, required)

### Request Body

`UpdateAliasRequest`

### Response

`AliasResponse`

---

## DELETE /{alias_id}

Delete an alias.

### Path Parameters

- `alias_id` (string, required)

### Response

`AliasResponse`

---

## GET /get-by-name

Get an alias by name.

### Query Parameters

- `name` (string, required)
- `db_connection_id` (string, required)

### Response

`AliasResponse`