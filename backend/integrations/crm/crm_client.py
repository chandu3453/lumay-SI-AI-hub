"""CRM integration client — HTTP adapter for external CRM system."""

from integrations.base_client import BaseIntegrationClient


class CRMClient(BaseIntegrationClient):
    """
    Adapter for the external CRM system.
    Base URL configured via CRM_BASE_URL environment variable.
    """

    async def health_check(self) -> bool:
        try:
            await self._get("/health")
            return True
        except Exception:
            return False
