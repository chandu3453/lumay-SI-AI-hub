# Docker

## Quick Start

```bash
# Start all services
docker compose up -d

# Start specific services (development)
docker compose up -d postgres redis rabbitmq opensearch minio

# View logs
docker compose logs -f backend frontend

# Stop everything
docker compose down
```

## Services

Defined in `docker-compose.yml` at the project root. All data volumes are persisted under named Docker volumes (not bind mounts) for production safety.

## Building Images

```bash
# Backend
docker build -t lumay-backend:latest -f infrastructure/docker/Dockerfile.backend .

# Frontend
docker build -t lumay-frontend:latest -f infrastructure/docker/Dockerfile.frontend .
```

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Backend | Hot reload (`--reload`) | Multi-stage build, Gunicorn/Uvicorn |
| Frontend | `npm run dev` | Static export or Node server |
| Nginx | HTTP only | HTTPS with certbot |
| Volumes | Named volumes | Named volumes + S3 backup |
| Monitoring | Prometheus + Grafana | Prometheus + Grafana + Alertmanager |

## Volume Mounts

Configuration files mounted from `infrastructure/`:

| Service | Config Mount |
|---------|-------------|
| Nginx | `./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf` |
| PostgreSQL | `./infrastructure/postgres/conf/postgresql.conf:/etc/postgresql/postgresql.conf` |
| PostgreSQL Init | `./infrastructure/postgres/init/:/docker-entrypoint-initdb.d/` |
| Redis | `./infrastructure/redis/redis.conf:/usr/local/etc/redis/redis.conf` |
| RabbitMQ | `./infrastructure/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf` |
| OpenSearch | `./infrastructure/opensearch/opensearch.yml:/usr/share/opensearch/config/opensearch.yml` |
| MinIO | `./infrastructure/minio/config.json:/root/.minio/config.json` |
