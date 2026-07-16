"""
Platform layer — reusable shared infrastructure.

All platform components follow the same lifecycle pattern:
  init_*()   — called during application startup
  close_*()  — called during application shutdown
  get_*()    — returns the initialised client instance (raises if not initialised)

Public API:
  - auth:        JWTService, TokenPayload, TokenPair, get_current_user, CurrentUser
  - cache:       Redis client lifecycle + CacheService
  - database:    SQLAlchemy base models, session factory, repository, migration utils
  - health:      HealthCheckService and response schemas
  - logging:     structlog configuration
  - messaging:   RabbitMQ connection lifecycle + EventPublisher
  - monitoring:  OpenTelemetry tracing initialisation
  - search:      OpenSearch client lifecycle + BaseSearchService
  - security:    Role enum + require_roles dependency factory
  - settings:    Settings model re-export
  - storage:     MinIO client lifecycle + StorageService
"""
