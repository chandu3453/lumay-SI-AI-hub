# Project Documentation

## Structure

```
docs/
├── architecture/     System architecture and design decisions
│   ├── overview.md           High-level architecture description
│   ├── domain-model.md       Domain model and bounded contexts
│   ├── data-flow.md          Data flow diagrams and descriptions
│   └── decisions.md          Architectural decisions log
├── api/              API reference and integration guides
│   ├── overview.md           API conventions, versioning, pagination
│   ├── authentication.md     Authentication and authorisation
│   ├── errors.md             Error response format and codes
│   └── endpoints/            Per-resource endpoint documentation
├── database/         Database schema and operations
│   ├── overview.md           Database platform and conventions
│   ├── schema.md             Entity-relationship diagram and table docs
│   ├── migrations.md         Alembic migration workflow
│   └── indexes.md            Indexing strategy and query patterns
├── deployment/       Infrastructure and operations
│   ├── overview.md           Deployment architecture
│   ├── docker.md             Docker Compose services
│   ├── environments.md       Environment configuration reference
│   ├── monitoring.md         Monitoring, logging, alerting
│   └── ci-cd.md              CI/CD pipeline
├── adr/              Architecture Decision Records
│   ├── template.md           ADR template
│   └── 0001-*.md             Decision records
├── README.md         This file
└── CONTRIBUTING.md   Contribution guidelines
```

## Quick Links

- [Architecture Overview](architecture/overview.md)
- [API Conventions](api/overview.md)
- [Database Schema](database/overview.md)
- [Deployment Guide](deployment/overview.md)
- [ADR Index](adr/README.md)
- [Contributing](CONTRIBUTING.md)
