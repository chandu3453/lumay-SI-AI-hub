# Deployment Overview

## Architecture

```
                        ┌─────────┐
                        │  CDN    │
                        └────┬────┘
                             │
                        ┌────▼────┐
                        │  Nginx  │  ─── SSL, rate limiting, reverse proxy
                        └────┬────┘
                   ┌─────────┴──────────┐
                   ▼                    ▼
            ┌──────────┐        ┌──────────┐
            │  FastAPI  │        │  Next.js │
            │  Backend  │        │ Frontend │
            └─────┬─────┘        └──────────┘
                  │
     ┌────────────┼────────────┬────────────┐
     ▼            ▼            ▼            ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐
│Postgres│ │  Redis  │ │ RabbitMQ │ │MinIO   │
│  16    │ │    7    │ │    3     │ │Object  │
└────────┘ └─────────┘ └──────────┘ │Storage │
                              ┌─────┴────────┐
                              │  OpenSearch  │
                              │  2.x         │
                              └──────────────┘
```

## Environments

| Environment | URL | Notes |
|-------------|-----|-------|
| Development | `http://localhost:3000` | Local Docker Compose |
| Staging | `https://staging.lumay-si.ai` | Production-like infra |
| Production | `https://lumay-si.ai` | HA configuration |

## Service Overview

| Service | Port (internal) | Replicas | Persistence |
|---------|----------------|----------|-------------|
| Nginx | 80/443 | 1 | Config only |
| FastAPI Backend | 8000 | 2+ | None |
| Next.js Frontend | 3000 | 1+ | None |
| PostgreSQL | 5432 | 1 | Volume (persistent) |
| Redis | 6379 | 1 | Volume (AOF) |
| RabbitMQ | 5672/15672 | 1 | Volume |
| OpenSearch | 9200/9600 | 1 | Volume |
| MinIO | 9000/9001 | 1 | Volume |
| pgAdmin | 5050 | 1 | Volume (dev only) |
| Prometheus | 9090 | 1 | Volume |
| Grafana | 3001 | 1 | Volume |

## Health Checks

- **Liveness** (`/health/live`): Returns 200 if the process is alive.
- **Readiness** (`/health/ready`): Returns 200 if DB and cache are reachable.
- **Full** (`/health`): Returns status of all dependencies (DB, cache, search, storage).
