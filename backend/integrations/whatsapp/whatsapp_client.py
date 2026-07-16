"""WhatsApp integration client — adapter for WhatsApp Business API."""

from integrations.base_client import BaseIntegrationClient


class WhatsAppClient(BaseIntegrationClient):
    """
    Adapter for WhatsApp Business Cloud API.
    Base URL: https://graph.facebook.com/v18.0
    """

    async def health_check(self) -> bool:
        try:
            await self._get("/")
            return True
        except Exception:
            return False
