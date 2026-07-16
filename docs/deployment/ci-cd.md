# CI/CD Pipeline

## Pipeline Overview

```
Commit → Lint → Test → Build → Deploy Staging → E2E → Deploy Production
```

## CI (GitHub Actions)

### Backend

```yaml
# .github/workflows/backend.yml
- name: Lint
  run: cd backend && ruff check .
- name: Type Check
  run: cd backend && mypy .
- name: Test
  run: cd backend && pytest
```

### Frontend

```yaml
# .github/workflows/frontend.yml
- name: Lint
  run: cd frontend && npx biome check src/
- name: Type Check
  run: cd frontend && npx tsc --noEmit
- name: Test
  run: cd frontend && npx vitest run
```

## CD (Deployment)

### Staging

Deploys automatically on merge to `main`:

1. Build Docker images.
2. Push to container registry.
3. SSH to staging host.
4. Pull images and restart services.
5. Run database migrations.
6. Smoke test health endpoints.

### Production

Deploys manually via GitHub releases:

1. Create a release tag (`v1.2.3`).
2. CI builds and pushes images tagged with the version.
3. CI triggers production deployment workflow.
4. Blue-green deployment with health check verification.
5. Rollback on failure (previous images retained).

## Quality Gates

| Gate | Tool | Threshold |
|------|------|-----------|
| Linting | ruff / biome | Zero warnings |
| Type Check | mypy / tsc | Zero errors |
| Unit Tests | pytest / vitest | 80%+ coverage |
| Integration Tests | pytest | All passing |
| Security Scan | bandit / npm audit | Zero high/CVEs |
| Build | Docker | Successful |
