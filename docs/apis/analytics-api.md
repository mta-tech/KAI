# Analytics API Documentation

API for performing statistical analysis.

**Base URL:** `/api/v2/analytics`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/descriptive` | Get descriptive statistics |
| POST | `/descriptive/export` | Export descriptive statistics |
| POST | `/t-test` | Perform a t-test |
| POST | `/t-test/export` | Export t-test results |
| POST | `/correlation` | Perform a correlation analysis |
| POST | `/correlation/export` | Export correlation analysis results |
| POST | `/correlation-matrix` | Get a correlation matrix |
| POST | `/correlation-matrix/export` | Export a correlation matrix |
| POST | `/anomalies` | Detect anomalies |
| POST | `/anomalies/export` | Export anomaly detection results |
| POST | `/forecast` | Generate a forecast |
| POST | `/forecast/export` | Export forecast results |

---

## Data Types

This API uses a variety of request and response models. Please refer to the `openapi.json` file for detailed schema information.

---

## POST /descriptive

Get descriptive statistics.

### Request Body

`DescriptiveStatsRequest`

### Response

`DescriptiveStatsResponse`

---

## POST /descriptive/export

Export descriptive statistics.

### Request Body

`DescriptiveStatsExportRequest`

### Response

File download (JSON, CSV, or PDF)

---

## POST /t-test

Perform a t-test.

### Request Body

`TTestRequest`

### Response

`StatisticalTestResponse`

---

## POST /t-test/export

Export t-test results.

### Request Body

`TTestExportRequest`

### Response

File download (JSON, CSV, or PDF)

---

## POST /correlation

Perform a correlation analysis.

### Request Body

`CorrelationRequest`

### Response

`CorrelationResponse`

---

## POST /correlation/export

Export correlation analysis results.

### Request Body

`CorrelationExportRequest`

### Response

File download (JSON, CSV, or PDF)

---

## POST /correlation-matrix

Get a correlation matrix.

### Request Body

`CorrelationMatrixRequest`

### Response

`CorrelationMatrixResponse`

---

## POST /correlation-matrix/export

Export a correlation matrix.

### Request Body

`CorrelationMatrixExportRequest`

### Response

File download (JSON, CSV, or PDF)

---

## POST /anomalies

Detect anomalies.

### Request Body

`AnomalyRequest`

### Response

`AnomalyResponse`

---

## POST /anomalies/export

Export anomaly detection results.

### Request Body

`AnomalyExportRequest`

### Response

File download (JSON, CSV, or PDF)

---

## POST /forecast

Generate a forecast.

### Request Body

`ForecastRequest`

### Response

`ForecastResponse`

---

## POST /forecast/export

Export forecast results.

### Request Body

`ForecastExportRequest`

### Response

File download (JSON, CSV, or PDF)