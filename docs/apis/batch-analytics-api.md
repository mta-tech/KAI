# Batch Analytics API Documentation

API for managing batch analytics jobs.

**Base URL:** `/api/v2/analytics/batch`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create a new batch job |
| GET | `/{batch_id}` | Get the status of a batch job |
| DELETE | `/{batch_id}` | Delete a batch job |
| GET | `/{batch_id}/results` | Get the results of a batch job |

---

## Data Types

This API uses a variety of request and response models. Please refer to the `openapi.json` file for detailed schema information.

---

## POST /

Create a new batch job.

### Request Body

`AnalyticsBatchRequest`

### Response

`AnalyticsBatchStatus`

---

## GET /{batch_id}

Get the status of a batch job.

### Path Parameters

- `batch_id` (string, required)

### Response

`AnalyticsBatchStatus`

---

## DELETE /{batch_id}

Delete a batch job.

### Path Parameters

- `batch_id` (string, required)

### Response

`{}`

---

## GET /{batch_id}/results

Get the results of a batch job.

### Path Parameters

- `batch_id` (string, required)

### Response

`AnalyticsBatchResult`