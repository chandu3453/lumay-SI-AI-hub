"""
LuMay SMART Insurance AI Hub — FastAPI application package.

Architecture:
  config/       — Pydantic Settings loading and validation
  dependencies/ — FastAPI dependency injection providers
  middleware/    — ASGI middleware (correlation ID, request logging, security)
  routers/      — App-level routers (health, root)
  startup/      — Bootstrap lifecycle orchestration

Domain modules live under domains/ and are registered via app.main.
"""
