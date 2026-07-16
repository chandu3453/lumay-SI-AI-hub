"""Email integration client — SMTP via async Python."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.config.settings import get_settings
from app.platform.logging import get_logger
from integrations.base_client import BaseIntegrationClient

logger = get_logger(__name__)


class EmailClient:
    """
    Async SMTP email client.
    Handles HTML and plain-text email dispatch with TLS.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> None:
        """Sends an email via SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._settings.email_from_address
        msg["To"] = to

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=self._settings.smtp_host,
            port=self._settings.smtp_port,
            username=self._settings.smtp_user,
            password=self._settings.smtp_password,
            use_tls=self._settings.smtp_tls,
        )
        logger.info("email_sent", to=to, subject=subject)

    async def health_check(self) -> bool:
        try:
            async with aiosmtplib.SMTP(
                hostname=self._settings.smtp_host,
                port=self._settings.smtp_port,
            ) as smtp:
                await smtp.noop()
            return True
        except Exception:
            return False
