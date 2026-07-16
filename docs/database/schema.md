# Database Schema

## Entity-Relationship Diagram

```
┌──────────────┐     ┌───────────────┐
│    users     │     │   customers   │
├──────────────┤     ├───────────────┤
│ id (PK)      │     │ id (PK)       │
│ email        │     │ external_id   │
│ password_hash│     │ name          │
│ display_name │     │ email         │
│ is_active    │     │ phone         │
│ created_at   │     │ date_of_birth │
│ updated_at   │     │ is_active     │
└──────┬───────┘     └───────┬───────┘
       │                     │
       │  ┌──────────────────┘
       │  │
       │  │  ┌──────────────────┐
       │  │  │   complaints     │
       │  │  ├──────────────────┤
       │  │  │ id (PK)          │
       │  └──│ customer_id (FK) │
       │     │ assigned_to (FK) │
       │     │ category         │
       │     │ sub_category     │
       │     │ issue_type       │
       │     │ description      │
       │     │ status           │
       │     │ severity         │
       │     │ filed_at         │
       │     │ resolved_at      │
       │     │ metadata (JSONB) │
       │     ├──────────────────┤
       │     │ interactions     │
       │     ├──────────────────┤
       │     │ id (PK)          │
       │     │ complaint_id(FK) │
       │     │ type             │
       │     │ direction        │
       │     │ content          │
       │     │ conducted_at     │
       └─────┴──────────────────┘
```

## Key Tables

### users (schema: identity)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| display_name | VARCHAR(150) | NOT NULL |
| is_active | BOOLEAN | NOT NULL, DEFAULT true |
| last_login_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

### complaints (schema: complaint)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| customer_id | UUID | FK → customers.id, NOT NULL |
| assigned_to | UUID | FK → users.id, NULLABLE |
| category | VARCHAR(100) | NOT NULL |
| sub_category | VARCHAR(100) | NOT NULL |
| issue_type | VARCHAR(200) | NOT NULL |
| description | TEXT | NOT NULL |
| status | complaint_status | NOT NULL, DEFAULT 'filed' |
| severity | severity_level | NOT NULL, DEFAULT 'medium' |
| sentiment_label | VARCHAR(20) | NULLABLE |
| sentiment_score | REAL | NULLABLE |
| filed_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| resolved_at | TIMESTAMPTZ | NULLABLE |
| metadata | JSONB | NOT NULL, DEFAULT '{}' |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

### audit_log (schema: audit)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| actor_id | UUID | FK → users.id, NULLABLE (for system actions) |
| action | VARCHAR(100) | NOT NULL |
| resource_type | VARCHAR(100) | NOT NULL |
| resource_id | UUID | NOT NULL |
| old_values | JSONB | NULLABLE |
| new_values | JSONB | NULLABLE |
| ip_address | INET | NULLABLE |
| user_agent | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

## Constraints and Indexes

All tables have:
- Primary key on `id` (UUID, clustered)
- Index on `created_at` (for time-based queries)
- Index on `updated_at` (for change-tracking queries)
- Foreign key constraints where applicable

Domain-specific indexes are defined in `infrastructure/postgres/init/03-performance.sql`.
