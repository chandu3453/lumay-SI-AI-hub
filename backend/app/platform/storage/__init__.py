"""Storage platform — MinIO client lifecycle and StorageService."""

from app.platform.storage.client import (
    StorageService,
    UploadResult,
    close_storage_client,
    get_storage_client,
    init_storage_client,
)

__all__ = [
    "close_storage_client",
    "get_storage_client",
    "init_storage_client",
    "StorageService",
    "UploadResult",
]
