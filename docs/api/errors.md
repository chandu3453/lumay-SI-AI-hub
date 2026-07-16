# API Errors

## Error Response Format

All errors return a consistent envelope:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "context": {
    "errors": [
      {"field": "email", "message": "value is not a valid email address"}
    ]
  }
}
```

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `VALIDATION_ERROR` | Request body or query validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 401 | `TOKEN_EXPIRED` | Access token has expired |
| 403 | `FORBIDDEN` | Authenticated but insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource state conflict (e.g., duplicate email) |
| 422 | `VALIDATION_ERROR` | Request body schema validation failed |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Dependency unhealthy |

## Validation Errors (422)

Field-level errors are returned in `context.errors`:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "context": {
    "errors": [
      {"field": "email", "message": "value is not a valid email address"},
      {"field": "password", "message": "String should have at least 8 characters"}
    ]
  }
}
```

## Health Check Response

```
GET /health
```

**Response 200 (healthy):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-04-15T14:30:00Z",
  "dependencies": [
    {"name": "postgresql", "status": "healthy", "latency_ms": 2.34},
    {"name": "redis", "status": "healthy", "latency_ms": 1.12},
    {"name": "opensearch", "status": "healthy", "latency_ms": 5.67},
    {"name": "minio", "status": "healthy", "latency_ms": 3.45}
  ]
}
```

**Response 503 (unhealthy):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-04-15T14:30:05Z",
  "dependencies": [
    {"name": "postgresql", "status": "healthy", "latency_ms": 2.10},
    {"name": "redis", "status": "unhealthy", "error": "Connection refused"}
  ]
}
```
