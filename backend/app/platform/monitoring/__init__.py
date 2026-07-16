"""Monitoring platform — OpenTelemetry tracing initialisation."""

from app.platform.monitoring.tracer import init_tracing, shutdown_tracing

__all__ = ["init_tracing", "shutdown_tracing"]
