# lumay-si-ai-hub

**Enterprise AI-Powered Insurance Complaints & Sentiment Intelligence Platform**

---

## Overview

`lumay-si-ai-hub` is a modular monolith enterprise platform for managing insurance complaints, customer interactions, and sentiment intelligence using AI. The architecture is designed for future extraction into microservices.

---

## Tech Stack

### Frontend
- Next.js 15 + React 19 + TypeScript
- TailwindCSS + shadcn/ui
- Zustand · TanStack Query · React Hook Form · Zod

### Backend
- Python 3.13 + FastAPI
- SQLAlchemy 2 + Alembic + Pydantic v2
- Uvicorn

### Infrastructure
- PostgreSQL · Redis · RabbitMQ · OpenSearch · MinIO
- Docker + Docker Compose · Nginx

### AI Stack
- LangGraph · Azure OpenAI · OpenAI
- NeMo Guardrails · Microsoft Presidio · Instructor

---

## Architecture

Modular Monolith — business logic is separated into autonomous domains with clean boundaries. AI capabilities are isolated from business domains. The platform layer provides shared infrastructure abstractions.

```
lumay-si-ai-hub/
├── backend/          # FastAPI modular monolith
├── frontend/         # Next.js 15 SPA
├── infrastructure/   # Docker, Nginx, service configs
├── docs/             # Architecture, API, DB, ADR
├── scripts/          # Dev and ops utilities
├── tests/            # Integration and E2E tests
└── .github/          # CI/CD workflows
```

---

## Quick Start

### Prerequisites
- Docker 24+
- Docker Compose 2.20+
- Node.js 20+
- Python 3.13+

### 1. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Infrastructure
```bash
docker compose up -d postgres redis rabbitmq opensearch minio
```

### 3. Run Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Full Stack (Docker)
```bash
docker compose up --build
```

---

## Development

| Service       | URL                        |
|---------------|----------------------------|
| Frontend      | http://localhost:3000       |
| Backend API   | http://localhost:8000       |
| API Docs      | http://localhost:8000/docs  |
| MinIO Console | http://localhost:9001       |
| RabbitMQ UI   | http://localhost:15672      |

---

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [API Reference](docs/api/)
- [Database Schema](docs/database/)
- [Deployment Guide](docs/deployment/)
- [Architecture Decision Records](docs/adr/)

---

## License

Proprietary — All rights reserved.


-------------
Running the Application

1. Start Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

2. Start Frontend
cd frontend
npm run dev

3. Access
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:3000
