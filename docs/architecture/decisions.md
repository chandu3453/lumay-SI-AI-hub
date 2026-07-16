# Architectural Decisions Log

This document captures significant architectural decisions made during the project. For individual decisions with full context, see the [ADR directory](../adr/).

## Summary

| Decision | Status | Date |
|----------|--------|------|
| Modular monolith over microservices | Accepted | 2025-04 |
| PostgreSQL with async SQLAlchemy | Accepted | 2025-04 |
| RabbitMQ for async messaging | Accepted | 2025-04 |
| OpenSearch for search and vector store | Accepted | 2025-04 |
| MinIO for object storage | Accepted | 2025-04 |
| Redis for caching | Accepted | 2025-04 |
| JWT bearer token auth | Accepted | 2025-04 |
| Structlog for structured logging | Accepted | 2025-04 |
| OpenTelemetry for distributed tracing | Accepted | 2025-04 |
| AI pipeline via AIGateway facade | Accepted | 2025-04 |

## Key Rationale

### Modular Monolith
- **Chosen over**: Microservices, serverless functions.
- **Why**: Team size is small; deployment complexity of microservices outweighs benefits at this stage. Domain boundaries are clearly separated in code, allowing future extraction to services if needed.
- **Trade-off**: Single deployment unit; all domains scale together.

### PostgreSQL + async SQLAlchemy
- **Chosen over**: MongoDB, MySQL, synchronous ORM.
- **Why**: Relational integrity is critical for insurance data; async avoids blocking during I/O; SQLAlchemy provides migration tooling (Alembic) and repository pattern support.

### AI Gateway Facade
- **Chosen over**: Direct provider calls from domains.
- **Why**: Isolates AI provider selection, prompt versioning, and guardrail execution from domain logic. Allows swapping providers without touching business code.
