# Environment Configuration

## Configuration Model

All configuration is managed through Pydantic Settings v2 (`app.config.settings.Settings`), loaded from environment variables or `.env` file.

## Environment Variables

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `lumay-si-ai-hub` | Application name |
| `APP_VERSION` | `1.0.0` | API version string |
| `APP_ENV` | `development` | `development`, `staging`, or `production` |
| `APP_SECRET_KEY` | (required) | Strong random secret for signing |
| `APP_DEBUG` | `false` | Enable debug mode (disabled in production) |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `json` | `json` or `console` (console for dev) |

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated origins |

### PostgreSQL

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | asyncpg connection string |
| `POSTGRES_POOL_SIZE` | `10` | Connection pool size |
| `POSTGRES_MAX_OVERFLOW` | `20` | Max overflow connections |
| `POSTGRES_ECHO` | `false` | Log all SQL statements |

### Redis

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `REDIS_MAX_CONNECTIONS` | `50` | Max connections |

### RabbitMQ

| Variable | Default | Description |
|----------|---------|-------------|
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | AMQP connection string |

### OpenSearch

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENSEARCH_URL` | `http://localhost:9200` | OpenSearch endpoint |
| `OPENSEARCH_USER` | `admin` | Basic auth username |
| `OPENSEARCH_PASSWORD` | `admin` | Basic auth password |
| `OPENSEARCH_USE_SSL` | `false` | Enable TLS |

### MinIO

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO server endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | Access key |
| `MINIO_SECRET_KEY` | `minioadmin` | Secret key |
| `MINIO_SECURE` | `false` | Use HTTPS |
| `MINIO_DEFAULT_BUCKET` | `lumay-documents` | Default bucket name |

### JWT

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | (required) | Strong random secret for JWT signing |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |

### Azure OpenAI

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | `https://...` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | `` | API key |
| `AZURE_OPENAI_API_VERSION` | `2024-02-01` | API version |
| `AZURE_OPENAI_DEPLOYMENT_GPT4` | `gpt-4o` | GPT-4 deployment name |
| `AZURE_OPENAI_DEPLOYMENT_EMBEDDING` | `text-embedding-3-large` | Embedding deployment |

### OpenTelemetry

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_ENABLED` | `false` | Enable tracing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OTLP gRPC endpoint |
| `OTEL_SERVICE_NAME` | `lumay-si-ai-hub` | Service name |
| `OTEL_ENVIRONMENT` | `development` | Deployment environment label |

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `FEATURE_AI_ENABLED` | `true` | Enable AI pipeline |
| `FEATURE_PII_REDACTION` | `true` | Enable PII redaction guardrail |
| `FEATURE_SENTIMENT_ANALYSIS` | `true` | Enable sentiment pipeline |
| `FEATURE_AUDIT_LOG` | `true` | Enable audit logging |

## `.env` File

Copy `.env.example` and fill in secrets:

```bash
cp .env.example .env
```

Never commit `.env` to version control.
