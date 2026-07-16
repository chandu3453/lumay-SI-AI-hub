# API Overview

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Staging**: `https://staging.lumay-si.ai/api/v1`
- **Production**: `https://api.lumay-si.ai/api/v1`

## Conventions

### Request / Response Format

All requests and responses use `application/json` (JSON). The API uses `ORJSONResponse` for performance.

### Authentication

All endpoints except `POST /auth/login` and `POST /auth/register` require a Bearer JWT token:

```
Authorization: Bearer <access_token>
```

See [authentication.md](authentication.md) for details.

### Pagination

List endpoints support cursor-based pagination:

**Request:**
```
GET /complaints?cursor=2025-04-01T00:00:00Z&limit=50
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "2025-04-15T00:00:00Z",
    "has_more": true,
    "total": 1234
  }
}
```

### Filtering

Query parameters:

```
GET /complaints?status=filed&category=claim_delay&assigned_to=<user_id>
```

### Sorting

`sort` parameter with optional `-` prefix for descending:

```
GET /complaints?sort=-created_at
GET /complaints?sort=status,+created_at
```

### Dates

All timestamps are ISO 8601 in UTC: `2025-04-15T14:30:00Z`

## Versioning

The API is versioned via URL prefix (`/api/v1`). Breaking changes introduce a new version (`/api/v2`). Older versions are deprecated with a sunset header.

## Rate Limiting

- **Authenticated**: 100 requests/minute
- **Unauthenticated**: 10 requests/minute (login, register only)

Rate limit headers are returned on every response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1689456000
```

## Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Authenticate user | No |
| POST | `/auth/register` | Create account | No |
| POST | `/auth/refresh` | Refresh access token | Refresh |
| POST | `/auth/logout` | Invalidate tokens | Yes |
| GET | `/users/me` | Current user profile | Yes |
| PATCH | `/users/me` | Update profile | Yes |
| GET | `/complaints` | List complaints | Yes |
| POST | `/complaints` | File a complaint | Yes |
| GET | `/complaints/{id}` | Get complaint detail | Yes |
| PATCH | `/complaints/{id}` | Update complaint | Yes |
| GET | `/customers` | List customers | Yes |
| POST | `/customers` | Create customer | Yes |
| GET | `/customers/{id}` | Get customer detail | Yes |
| GET | `/analytics/dashboard` | Dashboard KPIs | Yes |
| GET | `/analytics/reports/{id}` | Get report | Yes |
| GET | `/search` | Full-text search | Yes |
| GET | `/health` | Full health check | No |
| GET | `/health/live` | Liveness probe | No |
| GET | `/health/ready` | Readiness probe | No |
