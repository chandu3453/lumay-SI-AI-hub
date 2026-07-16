"""
Base Integration Client.

All external system clients extend this abstract base.
Provides standardised retry logic, timeout handling, and error wrapping.
"""

from abc import ABC, abstractmethod

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.platform.logging import get_logger

logger = get_logger(__name__)


class BaseIntegrationClient(ABC):
    """Abstract base for all HTTP-based integration clients."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 30,
    ) -> None:
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds),
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _get(self, path: str, **kwargs) -> httpx.Response:  # type: ignore[type-arg]
        response = await self._client.get(path, **kwargs)
        response.raise_for_status()
        return response

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _post(self, path: str, **kwargs) -> httpx.Response:  # type: ignore[type-arg]
        response = await self._client.post(path, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    async def health_check(self) -> bool:
        """Returns True if the external system is reachable."""
        ...
