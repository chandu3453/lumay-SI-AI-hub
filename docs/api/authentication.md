# Authentication

## Token-Based Auth (JWT)

The API uses JWT bearer tokens for authentication. Two tokens are issued on login:

| Token | Lifetime | Usage |
|-------|----------|-------|
| Access Token | 30 minutes | Included in `Authorization` header for API calls |
| Refresh Token | 7 days | Exchanged for a new access token via `POST /auth/refresh` |

## Login

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "agent@example.com",
  "password": "your-password"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Using the Access Token

Include the token in all authenticated requests:

```
GET /api/v1/complaints
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Refreshing Tokens

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response 200:** Returns a new `TokenPair` (access + refresh).

## Logout

```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

Invalidates the current token pair (adds to blocklist).

## Token Payload

```json
{
  "sub": "user-uuid",
  "email": "agent@example.com",
  "roles": ["agent"],
  "jti": "unique-token-id",
  "exp": 1689456000,
  "iat": 1689454200,
  "kind": "access"
}
```

## Role-Based Access Control

| Role | Permissions |
|------|-------------|
| `super_admin` | Full system access, user management, configuration |
| `admin` | All data access, user management (except roles) |
| `analyst` | Read access, report generation, dashboard |
| `agent` | Complaint management, customer lookup, interactions |
| `auditor` | Read-only access, audit log access |
| `readonly` | Dashboard and report viewing only |

Use the `require_roles` dependency to gate endpoints:
```python
@router.get("/admin", dependencies=[Depends(require_roles(Role.ADMIN))])
```
