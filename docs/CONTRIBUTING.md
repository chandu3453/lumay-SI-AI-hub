# Contributing

## Development Setup

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in required values.
3. Start infrastructure services:
   ```bash
   docker compose up -d postgres redis rabbitmq opensearch minio
   ```
4. Install backend dependencies:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
6. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```
7. Start development servers:
   ```bash
   # Terminal 1 — backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # Terminal 2 — frontend
   cd frontend
   npm run dev
   ```

## Code Conventions

### Python (Backend)

- **Framework**: FastAPI with async views.
- **Architecture**: Modular monolith following Domain-Driven Design.
- **Style**: `ruff` for linting and formatting (line length 100).
- **Typing**: Strict type annotations everywhere; run `mypy --strict` before committing.
- **Imports**: Standard library → third-party → internal; absolute imports preferred.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- **Domain structure**: Each domain has `models/`, `schemas/`, `repositories/`, `services/`, `routers/`, `events/`, `exceptions/`, `constants/`.

### TypeScript (Frontend)

- **Framework**: Next.js 15 with React 19, shadcn/ui.
- **Style**: Biome for linting and formatting.
- **Typing**: Strict TypeScript; `tsc --noEmit` must pass.
- **Imports**: Use `@/` path alias for `src/`.
- **State**: Zustand for client state; React Query for server state.
- **Components**: One component per file; colocate tests.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): description
fix(scope): description
refactor(scope): description
docs(scope): description
chore(scope): description
```

## Pull Request Process

1. Create a feature branch from `main`.
2. Write or update tests for your changes.
3. Ensure all checks pass:
   ```bash
   cd backend && ruff check . && mypy .
   cd frontend && npx tsc --noEmit && npx vitest run
   ```
4. Open a pull request with a clear description.
5. Request review from at least one maintainer.

## Testing

- **Backend**: `pytest` with `pytest-asyncio`.
- **Frontend**: `vitest` with `@testing-library/react`.
- **E2E**: Playwright (integration tests in `tests/e2e/`).

Run the full test suite before pushing:
```bash
cd backend && pytest
cd frontend && npx vitest run
```
