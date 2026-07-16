# ==================================================
# lumay-si-ai-hub Backend Dockerfile
# Multi-stage build for development and production
# ==================================================

# ---- Base Stage ----
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies Stage ----
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Development Stage ----
FROM dependencies AS development

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev,voice]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]

# ---- Production Stage ----
FROM dependencies AS production

COPY . .

# Create non-root user
RUN groupadd -r lumay && useradd -r -g lumay lumay
RUN chown -R lumay:lumay /app
USER lumay

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "warning"]
