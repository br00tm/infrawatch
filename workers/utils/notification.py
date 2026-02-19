"""Notification utilities for sending alerts."""

import asyncio
from typing import Optional

import httpx
from celery.utils.log import get_task_logger

from config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()


def send_notification(channel: str, message: str) -> bool:
    """Send notification to specified channel."""
    handlers = {
        "telegram": send_telegram,
        "discord": send_discord,
        "email": send_email,
        "webhook": send_webhook,
    }

    handler = handlers.get(channel)
    if handler:
        return handler(message)
    else:
        logger.warning(f"Unknown notification channel: {channel}")
        return False


def send_telegram(message: str) -> bool:
    """Send notification via Telegram."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram not configured")
        return False

    try:
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": settings.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10)
            response.raise_for_status()

        logger.info("Telegram notification sent successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False


def send_discord(message: str) -> bool:
    """Send notification via Discord webhook."""
    if not settings.discord_webhook_url:
        logger.warning("Discord webhook not configured")
        return False

    try:
        payload = {
            "content": message,
            "username": "InfraWatch",
        }

        with httpx.Client() as client:
            response = client.post(
                settings.discord_webhook_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()

        logger.info("Discord notification sent successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False


def send_email(message: str, to_email: Optional[str] = None) -> bool:
    """Send notification via email."""
    if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password]):
        logger.warning("Email not configured")
        return False

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = settings.email_from or settings.smtp_user
        msg["To"] = to_email or settings.smtp_user
        msg["Subject"] = "InfraWatch Alert"

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        logger.info("Email notification sent successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False


def send_webhook(message: str, webhook_url: Optional[str] = None) -> bool:
    """Send notification via generic webhook."""
    url = webhook_url
    if not url:
        logger.warning("Webhook URL not provided")
        return False

    try:
        payload = {
            "source": "infrawatch",
            "message": message,
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10)
            response.raise_for_status()

        logger.info("Webhook notification sent successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to send webhook notification: {e}")
        return False
