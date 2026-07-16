"""
LuMay SMART Insurance AI Hub — FastAPI application entry point.

Application factory creates, configures, and returns a FastAPI instance.
All middleware, routers, exception handlers, and the lifespan are
registered here. Domain routers are registered via lazy imports
wrapped in try/except to allow incremental domain enablement.

Usage:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import get_settings
from app.config.environment import Environment
from app.lifespan import lifespan_handler
from app.middleware import CombinedASGIMiddleware
from app.platform.logging import get_logger
from app.routers import health_router, root_router
from shared.exceptions.handlers import register_exception_handlers

logger = get_logger(__name__)
settings = get_settings()


def create_app() -> FastAPI:
    is_production = settings.application.environment == Environment.PRODUCTION
    app = FastAPI(
        title=settings.application.name,
        description="Enterprise AI-powered Insurance Complaints & Sentiment Intelligence Platform",
        version=settings.application.version,
        docs_url="/docs" if not is_production else None,
        redoc_url="/redoc" if not is_production else None,
        openapi_url="/openapi.json" if not is_production else None,
        lifespan=lifespan_handler,
    )

    _register_middleware(app)
    _register_routers(app)
    register_exception_handlers(app)

    logger.info(
        "application_created",
        name=settings.application.name,
        version=settings.application.version,
        env=settings.application.environment,
    )
    return app


def _register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allowed_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # NOTE: BaseHTTPMiddleware-based middlewares replaced with ASGI version
    # to avoid blocking responses with long-running background tasks.
    # See VoiceRuntime.start_pipeline which runs as asyncio.create_task.

    from app.middleware.asgi_combined import CombinedASGIMiddleware
    app.add_middleware(CombinedASGIMiddleware)


def _register_routers(app: FastAPI) -> None:
    app.include_router(root_router, tags=["Root"])
    app.include_router(health_router, tags=["Health"])

    try:
        from fastapi.responses import FileResponse
        from pathlib import Path

        _test_html = Path(__file__).resolve().parent.parent / "voice_test.html"
        if _test_html.exists():

            @app.get("/voice-test", include_in_schema=False)
            async def voice_test_page():
                return FileResponse(
                    str(_test_html),
                    media_type="text/html",
                    headers={
                        "Permissions-Policy": "microphone=(self), camera=(self)",
                    },
                )

            logger.info("voice_test_page_mounted", path=str(_test_html))

        _static_dir = Path(__file__).resolve().parent.parent / "static"
        if _static_dir.exists():
            from fastapi.staticfiles import StaticFiles
            app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
            logger.info("static_files_mounted", path=str(_static_dir))
    except Exception as exc:
        logger.warning("voice_test_page_unavailable", error=str(exc))

    _register_domain_routers(app)

    try:
        from app.demo.routers import router as demo_router
        app.include_router(demo_router, prefix="/api/v1")
        logger.debug("demo_router_registered")
    except (ImportError, AttributeError):
        logger.debug("demo_router_unavailable")

    try:
        from voice.router import router as voice_router
        app.include_router(voice_router, prefix="/api/v1")
        voice_count = sum(1 for r in app.routes if hasattr(r, 'path') and 'voice' in r.path)
        logger.info("voice_router_registered", voice_routes=voice_count)
    except Exception as exc:
        logger.warning("voice_router_unavailable", error=str(exc), exc_info=True)


def _register_domain_routers(app: FastAPI) -> None:
    domain_routers: list[tuple[str, str]] = [
        ("domains.identity.routers", "auth_router"),
        ("domains.identity.routers", "user_router"),
        ("domains.customer.routers", "customer_router"),
        ("domains.complaint.routers", "complaint_router"),
        ("domains.interaction.routers", "interaction_router"),
        ("domains.workflow.routers", "workflow_router"),
        ("domains.notification.routers", "notification_router"),
        ("domains.analytics.routers", "analytics_router"),
        ("domains.search.routers", "search_router"),
        ("domains.audit.routers", "audit_router"),
        ("domains.knowledge.routers", "knowledge_router"),
        ("domains.configuration.routers", "configuration_router"),
    ]

    for module_path, router_name in domain_routers:
        try:
            import importlib

            module = importlib.import_module(module_path)
            router = getattr(module, router_name)
            app.include_router(router, prefix="/api/v1")
            logger.debug("domain_router_registered", module=module_path, router=router_name)
        except (ImportError, AttributeError):
            logger.debug("domain_router_unavailable", module=module_path)


app: FastAPI = create_app()
