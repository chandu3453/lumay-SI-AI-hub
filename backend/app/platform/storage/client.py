"""
MinIO Object Storage Client.

Manages the MinIO client lifecycle and provides
a typed storage service for file uploads and downloads.
"""

import io
from dataclasses import dataclass
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_storage_client: Minio | None = None


async def init_storage_client() -> None:
    """Initialises the MinIO client. Bucket creation is deferred to first use."""
    global _storage_client

    settings = get_settings()

    _storage_client = Minio(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure,
    )

    logger.info("minio_client_initialized", endpoint=settings.minio.endpoint)


async def close_storage_client() -> None:
    """Cleans up the storage client reference."""
    global _storage_client
    _storage_client = None
    logger.info("minio_client_closed")


def get_storage_client() -> Minio:
    if _storage_client is None:
        raise RuntimeError("Storage client is not initialised. Call init_storage_client() first.")
    return _storage_client


def _ensure_bucket(bucket_name: str) -> None:
    client = get_storage_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        logger.info("minio_bucket_created", bucket=bucket_name)


@dataclass
class UploadResult:
    bucket: str
    object_name: str
    size: int
    etag: str


class StorageService:
    """
    High-level object storage service.
    Domain-specific storage adapters can extend this class.
    """

    def __init__(self, bucket_name: str) -> None:
        self._bucket = bucket_name

    def upload(
        self,
        object_name: str,
        data: BinaryIO,
        size: int,
        content_type: str = "application/octet-stream",
    ) -> UploadResult:
        """
        Uploads a file-like object to the configured bucket.

        Args:
            object_name: Path/name of the object within the bucket.
            data: File-like object (opened in binary read mode).
            size: Length of the data in bytes.
            content_type: MIME type of the object.
        """
        client = get_storage_client()
        result = client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=data,
            length=size,
            content_type=content_type,
        )
        return UploadResult(
            bucket=self._bucket,
            object_name=object_name,
            size=size,
            etag=result.etag,
        )

    def get_presigned_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Generates a presigned GET URL valid for the given duration."""
        from datetime import timedelta

        client = get_storage_client()
        return client.presigned_get_object(
            bucket_name=self._bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires_seconds),
        )

    def delete(self, object_name: str) -> None:
        """Removes an object from the bucket."""
        client = get_storage_client()
        client.remove_object(bucket_name=self._bucket, object_name=object_name)

    def ping(self) -> bool:
        """Tests connectivity by checking the bucket exists."""
        try:
            client = get_storage_client()
            return client.bucket_exists(self._bucket)
        except Exception:
            return False
