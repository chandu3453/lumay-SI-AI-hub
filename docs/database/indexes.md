# Database Indexes and Query Patterns

## Indexing Strategy

### Default Indexes (all tables)

```sql
CREATE INDEX idx_{table}_created_at ON {schema}.{table} (created_at DESC);
CREATE INDEX idx_{table}_updated_at ON {schema}.{table} (updated_at DESC);
```

### Complaint Table

```sql
-- Primary lookup patterns
CREATE INDEX idx_complaint_status ON complaint.complaints (status);
CREATE INDEX idx_complaint_customer ON complaint.complaints (customer_id);
CREATE INDEX idx_complaint_assigned ON complaint.complaints (assigned_to);
CREATE INDEX idx_complaint_category ON complaint.complaints (category);
CREATE INDEX idx_complaint_severity ON complaint.complaints (severity);
CREATE INDEX idx_complaint_filed_date ON complaint.complaints (filed_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_complaint_status_filed ON complaint.complaints (status, filed_at DESC);
CREATE INDEX idx_complaint_assigned_status ON complaint.complaints (assigned_to, status);

-- GIN index for JSONB metadata queries
CREATE INDEX idx_complaint_metadata ON complaint.complaints USING GIN (metadata);
```

### Audit Log

```sql
-- Time-range queries
CREATE INDEX idx_audit_created ON audit.audit_log (created_at DESC);

-- Resource lookup
CREATE INDEX idx_audit_resource ON audit.audit_log (resource_type, resource_id);

-- Actor lookup
CREATE INDEX idx_audit_actor ON audit.audit_log (actor_id);
```

### Full-Text Search

```sql
-- Complaint description search
CREATE INDEX idx_complaint_fts ON complaint.complaints
  USING GIN (to_tsvector('english', description));
```

## Common Query Patterns

### Dashboard — Open Complaints by Agent

```sql
SELECT u.display_name, COUNT(c.id) AS open_count
FROM complaint.complaints c
JOIN identity.users u ON u.id = c.assigned_to
WHERE c.status IN ('filed', 'in_review')
GROUP BY u.display_name
ORDER BY open_count DESC;
```

### Complaints by Category Over Time

```sql
SELECT
  category,
  DATE_TRUNC('month', filed_at) AS month,
  COUNT(*) AS count
FROM complaint.complaints
WHERE filed_at >= NOW() - INTERVAL '6 months'
GROUP BY category, DATE_TRUNC('month', filed_at)
ORDER BY month DESC, count DESC;
```

### SLA Breach Candidates

```sql
SELECT id, category, filed_at
FROM complaint.complaints
WHERE status IN ('filed', 'in_review')
  AND filed_at < NOW() - INTERVAL '48 hours'
ORDER BY filed_at ASC;
```

## Performance Notes

- All queries use parameterised bindings (no string interpolation).
- Use `EXPLAIN ANALYZE` before deploying new query patterns.
- The `pg_stat_statements` extension is enabled for identifying slow queries.
- Monitor `pg_stat_activity` for long-running transactions.
