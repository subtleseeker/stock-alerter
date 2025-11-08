"""Ntfy notifier implementation."""
import logging
import requests
from .base import Notifier
from ..models import Alert

logger = logging.getLogger(__name__)


class NtfyNotifier(Notifier):
    """Send notifications using ntfy."""

    def __init__(self, ntfy_url: str, topic: str, priority: str = "high"):
        """
        Initialize ntfy notifier.

        Args:
            ntfy_url: URL of the ntfy server (e.g., http://ntfy:80)
            topic: Topic to publish to
            priority: Priority level (default: high)
        """
        self.ntfy_url = ntfy_url.rstrip('/')
        self.topic = topic
        self.priority = priority

    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert via ntfy.

        Args:
            alert: Alert object to send

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            url = f"{self.ntfy_url}/{self.topic}"

            headers = {
                "Title": f"{alert.index_name} Alert",
                "Priority": self.priority,
                "Tags": "chart_with_downwards_trend,warning"
            }

            response = requests.post(
                url,
                data=alert.message.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            logger.info(f"Alert sent successfully to {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to send alert via ntfy: {e}")
            return False

    def send_status(self, title: str, message: str) -> bool:
        """
        Send a status/info message via ntfy.

        Args:
            title: Message title
            message: Message body

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            url = f"{self.ntfy_url}/{self.topic}"

            headers = {
                "Title": title,
                "Priority": "default",
                "Tags": "white_check_mark,information_source"
            }

            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            logger.info(f"Status message sent successfully to {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to send status message via ntfy: {e}")
            return False

    def send_error(self, title: str, message: str) -> bool:
        """
        Send an error notification via ntfy.

        Args:
            title: Error title
            message: Error message

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            url = f"{self.ntfy_url}/{self.topic}"

            headers = {
                "Title": title,
                "Priority": "high",
                "Tags": "x,rotating_light"
            }

            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            logger.info(f"Error notification sent successfully to {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to send error notification via ntfy: {e}")
            return False
