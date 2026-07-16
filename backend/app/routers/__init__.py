"""App-level routers (health, root, future domain routers)."""

from app.routers.health import router as health_router
from app.routers.root import router as root_router

__all__ = [
    "health_router",
    "root_router",
]
