"""Email delivery abstraction for login codes."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import boto3

from config.settings import settings

logger = logging.getLogger(__name__)


class EmailDelivery(ABC):
    @abstractmethod
    def send_login_code(self, *, email: str, code: str) -> None:
        raise NotImplementedError


class DevLogEmailDelivery(EmailDelivery):
    """Logs the login code for local/dev (never use as sole channel in production)."""

    def send_login_code(self, *, email: str, code: str) -> None:
        logger.info(
            "Login code for %s: %s",
            email,
            code,
            extra={"event": "auth.login_code.dev_log", "email": email},
        )


class SESEmailDelivery(EmailDelivery):
    """Amazon SES delivery for AWS environments."""

    def __init__(
        self,
        *,
        region: str | None = None,
        from_address: str | None = None,
    ) -> None:
        self._region = (region or settings.resolved_aws_region).strip()
        self._from = (from_address or settings.ses_from_email).strip()
        if not self._from:
            raise ValueError("SES_FROM_EMAIL is required when EMAIL_DELIVERY=ses")
        self._client = boto3.client("ses", region_name=self._region)

    def send_login_code(self, *, email: str, code: str) -> None:
        subject = "Your RRE sign-in code"
        body = (
            f"Your one-time sign-in code is: {code}\n\n"
            f"It expires in {settings.login_code_ttl_minutes} minutes.\n"
            "If you did not request this, ignore this email.\n"
        )
        self._client.send_email(
            Source=self._from,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        logger.info(
            "Login code emailed via SES",
            extra={"event": "auth.login_code.ses", "email": email},
        )


def build_email_delivery() -> EmailDelivery:
    provider = (settings.email_delivery or "dev_log").strip().lower()
    if provider in {"ses", "amazon_ses"}:
        return SESEmailDelivery()
    return DevLogEmailDelivery()


email_delivery: EmailDelivery = build_email_delivery()
