# Data Flow

## Complaint Processing Flow

```
                  ┌─────────────┐
                  │   Client    │
                  └──────┬──────┘
                         │ POST /api/v1/complaints
                         ▼
                  ┌─────────────┐
                  │   Nginx     │  ─── SSL termination, rate limiting
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   FastAPI   │  ─── Auth check, request validation
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Complaint  │  ─── Business logic, event publishing
                  │   Service   │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ AI Gateway  │  ─── Single entry to AI layer
                  └──────┬──────┘
                         │
                  ┌──────┴──────┐
                  │              │
                  ▼              ▼
          ┌──────────┐   ┌──────────┐
          │ PII Guard │   │   ...    │  ─── Input guardrails
          └──────────┘   └──────────┘
                  │
                  ▼
          ┌──────────────┐
          │  Complaint   │  ─── Classification + Sentiment +
          │  Pipeline    │       Severity pipelines
          └──────────────┘
                  │
                  ▼
          ┌──────────────┐
          │ Output Guard │  ─── Content safety check
          └──────────────┘
                  │
                  ▼
          ┌──────────────┐
          │  Evaluation  │  ─── Quality scoring
          └──────────────┘
                  │
                  ▼
          ┌─────────────┐
          │   Persist   │  ─── Store result in PostgreSQL
          └──────┬──────┘
                 │
                 ▼
          ┌─────────────┐
          │  Publish    │  ─── Emit ComplaintProcessed event
          │  Event      │
          └─────────────┘
                 │
          ┌──────┴──────┐
          ▼              ▼
   ┌──────────┐   ┌──────────┐
   │ RabbitMQ │   │  Redis   │  ─── Cache updated aggregates
   └──────────┘   └──────────┘
          │
          ▼
   ┌──────────────────────┐
   │ Notification Service │  ─── Email/SMS/Push to assigned agent
   └──────────────────────┘
```

## Authentication Flow

```
Client → Login (email + password)
  → POST /api/v1/auth/login
    → Verify password (bcrypt)
    → Issue JWT (access + refresh)
    → Return TokenPair
  → Subsequent requests
    → Authorization: Bearer <access_token>
    → FastAPI Depends(get_current_user)
      → Decode JWT → Validate → Return TokenPayload
```

## Event Flow

```
Service A → EventPublisher.publish(event)
  → RabbitMQ exchange (topic)
    → Queue (bound by routing key)
      → Consumer (another domain service)
        → Handle event → Execute side effect
```

Policies configured: retry (3 attempts, exponential backoff), DLQ after max retries.
