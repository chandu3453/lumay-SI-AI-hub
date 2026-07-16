# Monitoring

## Stack

| Component | Tool | Port |
|-----------|------|------|
| Metrics Collection | Prometheus | 9090 |
| Dashboards | Grafana | 3001 |
| Alerting | Alertmanager | 9093 |
| Logging | JSON stdout → Loki (planned) | — |
| Tracing | OpenTelemetry → OTLP collector | 4317 |

## Key Metrics

### Application

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, path, status | Total HTTP requests |
| `http_request_duration_ms` | Histogram | method, path | Request latency distribution |
| `complaints_processed_total` | Counter | category, status | Complaints processed |
| `ai_pipeline_duration_ms` | Histogram | pipeline_name | AI pipeline execution time |
| `ai_provider_latency_ms` | Histogram | provider | LLM provider response time |
| `db_query_duration_ms` | Histogram | operation | Database query latency |

### Infrastructure

| Metric | Source | Description |
|--------|--------|-------------|
| `pg_stat_activity` | PostgreSQL exporter | Active connections |
| `redis_memory_usage` | Redis exporter | Memory utilisation |
| `rabbitmq_queue_messages` | RabbitMQ exporter | Queue depth |
| `opensearch_cluster_status` | OpenSearch exporter | Cluster health |

## Dashboards (Grafana)

Pre-built dashboards are defined in `infrastructure/monitoring/grafana-dashboards/`.

### Available Dashboards

- **Application Overview**: Request rates, error rates, p95 latency, active users.
- **AI Pipeline Performance**: Pipeline execution times, provider latencies, guardrail pass rates.
- **Complaint Processing**: Complaints per category, resolution times, SLA compliance.
- **Infrastructure**: CPU/memory per service, DB connections, queue depth, storage usage.
