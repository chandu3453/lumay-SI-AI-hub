# Architecture Overview

## System Context

lumay-si-ai-hub is an AI-powered insurance complaints and sentiment intelligence platform. It processes incoming complaints through multi-stage AI pipelines (classification, sentiment analysis, PII redaction, severity scoring) and provides actionable insights via a dashboard interface.

## Architecture Style — Modular Monolith (DDD)

The backend is a modular monolith organised around domain boundaries:

```
┌──────────────────────────────────────────────────┐
│                    API Gateway                     │
│                  (FastAPI / Nginx)                 │
├──────────────────────────────────────────────────┤
│                    Domains                         │
│  ┌──────┐ ┌──────┐ ┌────────┐ ┌──────────────┐  │
│  │Identity││Customer││Complaint││ Interaction  │  │
│  └──────┘ └──────┘ └────────┘ └──────────────┘  │
│  ┌──────┐ ┌────┐ ┌──────┐ ┌──────┐ ┌────────┐  │
│  │Workflow││Notif││Analytics││Search││  Audit │  │
│  └──────┘ └────┘ └──────┘ └──────┘ └────────┘  │
│  ┌──────┐ ┌──────┐                               │
│  │Knowledge││Config│                               │
│  └──────┘ └──────┘                               │
├──────────────────────────────────────────────────┤
│                 Platform Layer                     │
│  Auth │ Cache │ DB │ Messaging │ Search │ Storage │
├──────────────────────────────────────────────────┤
│                     AI Layer                       │
│  Gateway │ Providers │ Pipelines │ Guardrails     │
├──────────────────────────────────────────────────┤
│               Infrastructure                       │
│  PG │ Redis │ RabbitMQ │ OpenSearch │ MinIO       │
└──────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Domains (11 bounded contexts)
Each domain contains its own models, schemas, repositories, services, routers, events, exceptions, and constants. Domains communicate via events.

### Platform Layer
Reusable infrastructure abstractions:
- **Auth**: JWT service, RBAC permissions, OAuth2 dependency injection.
- **Cache**: Redis connection pool management, typed `CacheService`.
- **Database**: Async SQLAlchemy engine, session factory, base repository, migration utilities.
- **Messaging**: RabbitMQ connection lifecycle, `EventPublisher`.
- **Search**: OpenSearch client lifecycle, `BaseSearchService`.
- **Storage**: MinIO client lifecycle, `StorageService`.
- **Health**: Aggregated health checks for all dependencies.
- **Logging**: Structlog configuration (JSON or console).
- **Security**: RBAC role definitions and `require_roles` dependency factory.

### AI Layer
Isolated intelligence layer consumed exclusively through the `AIGateway`:
- **Providers**: LLM adapters (Azure OpenAI, OpenAI, Anthropic).
- **Pipelines**: Domain-specific AI workflows (complaint, sentiment, classification).
- **Guardrails**: PII redaction, content safety, output validation.
- **Orchestrator**: LangGraph-based agentic workflows.
- **Memory**: Multi-turn conversation history.
- **Embeddings**: Text encoding and vector store management.
- **Retrieval**: RAG document retrieval and reranking.
- **Evaluation**: Response quality and safety metrics.

## Data Flow (Complaint Processing)

```
Client → Nginx → FastAPI → Complaint Router → Complaint Service
  → AI Gateway → Complaint Pipeline
      ├── PII Guard (input)
      ├── Classification Pipeline
      ├── Sentiment Pipeline
      ├── Content Safety Guard (output)
      └── Evaluation
  → Store Result → Publish Event → Notify
```
