# Database Overview

## Platform

| Property | Value |
|----------|-------|
| Engine | PostgreSQL 16 |
| Driver | `asyncpg` (via SQLAlchemy async) |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| UI | pgAdmin (development) |

## Connection

```
postgresql+asyncpg://lumay_user:password@localhost:5432/lumay_si_db
```

See `docker-compose.yml` for service definition and `.env` for credentials.

## Schema Conventions

All tables follow these conventions:

- **Primary Key**: UUID v4 (`id` column).
- **Timestamps**: `created_at` (server default `now()`), `updated_at` (auto-updated).
- **Soft Delete**: `is_deleted` (boolean), `deleted_at` (nullable timestamp) — used where required by regulation.
- **Naming**: `snake_case` table and column names; plural table names.

## Domain Schemas

The database is organised into PostgreSQL schemas matching domain boundaries:

| Schema | Tables | Purpose |
|--------|--------|---------|
| `identity` | `users`, `roles`, `user_roles`, `refresh_tokens` | Authentication and authorisation |
| `customer` | `customers`, `customer_addresses`, `customer_policies` | Customer profiles |
| `complaint` | `complaints`, `complaint_attachments`, `complaint_history` | Complaint records and lifecycle |
| `interaction` | `interactions`, `interaction_participants` | Communication history |
| `workflow` | `tasks`, `task_assignments`, `sla_policies` | Complaint routing and SLAs |
| `notification` | `notifications`, `notification_templates` | Outbound notifications |
| `analytics` | `reports`, `kpi_snapshots`, `dashboard_widgets` | Aggregated analytics |
| `search` | `search_index_log` | Search indexing metadata |
| `audit` | `audit_log` | Immutable action log |
| `knowledge` | `articles`, `article_categories` | Knowledge base |
| `configuration` | `settings`, `feature_flags` | System configuration |

## Extensions

Enabled in `infrastructure/postgres/init/01-extensions.sql`:

- `uuid-ossp` — UUID generation
- `pgcrypto` — Cryptographic functions
- `pg_stat_statements` — Query performance monitoring
