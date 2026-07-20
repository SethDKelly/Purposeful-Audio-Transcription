"""Email delivery abstraction for login codes."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

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


email_delivery: EmailDelivery = DevLogEmailDelivery()
