"""
OpenTelemetry Tracing Configuration.

Initialises OTEL SDK with OTLP exporter for distributed tracing.
Auto-instruments FastAPI and SQLAlchemy.
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)


async def init_tracing(service_name: str) -> None:
    """Initialises the OTEL tracer provider with OTLP export."""
    settings = get_settings()

    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: settings.application.version,
            "deployment.environment": settings.observability.otel_environment,
        }
    )

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.observability.otel_exporter_otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()

    logger.info("otel_tracing_initialized", service=service_name)


async def shutdown_tracing() -> None:
    """Flushes pending spans and shuts down the tracer provider."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()  # type: ignore[union-attr]
    logger.info("otel_tracing_shutdown")
