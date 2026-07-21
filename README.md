# LuMay SMART Insurance AI Hub

**Enterprise AI-Powered Insurance Complaints, State-Machine Conversations & Sentiment Intelligence Platform**

---

## Overview

`lumay-si-ai-hub` is a modular monolith enterprise platform for managing insurance complaints, customer interactions, and sentiment intelligence using AI. The architecture is designed for future extraction into microservices, isolating domain boundaries cleanly.

This project hosts the complete AI engine including:
* **Conversational Intent Engine (Sprint 27)**: A two-pass dialogue state machine that orchestrates sales, renewals, claims, complaints, and general inquiries dynamically.
* **Complaint Intelligence Pipeline**: Fully async background processing pipeline that extracts themes, sentiment, severity, root causes, and registers workflows & notifications.
* **Low-Latency Voice Integration**: Real-time voice assistance powered by LiveKit & Deepgram STT, optimized for rapid and natural consultative advisor responses.
* **AI Agent Assist**: Real-time co-pilot for human agents — suggested responses, live sentiment/context surfacing during active conversations.
* **Interaction Center**: Unified domain for tracking and managing customer interactions across channels.
* **Enterprise Analytics & Reporting**: Dedicated analytics and reporting domains for operational and business intelligence dashboards.

---

## Backend Domains

`backend/domains/` — each is an isolated bounded context with its own models, repositories, services, routers, and schemas:

| Domain | Purpose |
|---|---|
| `agent_assist` | AI-powered real-time assistance for human agents |
| `analytics` | Enterprise analytics and metrics |
| `audit` | Audit trail / activity logging |
| `complaint` | Complaint intake, triage, and intelligence pipeline |
| `configuration` | Platform/tenant configuration |
| `conversation` | Conversational state machine & dialogue engine |
| `customer` | Customer profile & account data |
| `identity` | Auth, users, roles & permissions |
| `interaction` | Cross-channel interaction/session tracking |
| `knowledge` | Knowledge base / RAG source content |
| `notification` | Notifications & alerting |
| `reporting` | Report generation |
| `search` | Search indexing & retrieval |
| `workflow` | Workflow orchestration & task routing |

`backend/ai/` hosts the AI engine itself (`orchestrator`, `pipelines`, `providers`, `gateway`, `guardrails`, `memory`, `retrieval`, `embeddings`, `evaluation`, `prompts`) — kept isolated from business domains per the modular-monolith boundary.

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

## Sprint 27 Architecture Highlights

1. **State Machine Dialogue Cache**: Tracks details collected during conversation (e.g. `policy_number`, `insurance_type`) to eliminate repetitive agent questions.
2. **Two-Pass Orchestration**:
   * **Pass 1**: Analyzes query intent and history, mapping dialogue progress.
   * **Pass 2**: Injects specific flow templates (Sales, renewals, claims, complaints, RAG) to generate responses.
3. **Optimized Latency**: Shifted heavy Complaint analysis and database logging to a background task using thread-safe, independent SQLite/DB connections, reducing turn response times from **13.5s to ~2.5s** (75%+ drop).
4. **Natural Speech Normalization**: Sanitizes and strips markdown elements from spoken agent text for natural TTS output, while keeping formatting pristine for chat interfaces.
5. **Fluid UI Inputs**: Textareas and input fields are completely interactive during response generation.

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
# Edit .env with your configuration keys (Azure OpenAI / OpenAI, LiveKit etc)
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
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 4. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Local Development Port Mapping

| Service       | URL                        |
|---------------|----------------------------|
| Frontend UI   | http://localhost:3000       |
| Customer Port | http://localhost:3001       |
| Backend API   | http://localhost:8001       |
| API Docs      | http://localhost:8001/docs  |
| MinIO Console | http://localhost:9001       |
| RabbitMQ UI   | http://localhost:15672      |

---

## License

Proprietary — All rights reserved.
