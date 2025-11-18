"""Ntfy notifier implementation."""
import logging
import requests
from .base import Notifier
from ..models import Alert

logger = logging.getLogger(__name__)


class NtfyNotifier(Notifier):
    """Send notifications using ntfy."""

    def __init__(self, ntfy_url: str, topic: str, priority: str = "high", critical_topic: str = None):
        """
        Initialize ntfy notifier.

        Args:
            ntfy_url: URL of the ntfy server (e.g., http://ntfy:80)
            topic: Topic to publish all alerts to
            priority: Priority level (default: high)
            critical_topic: Topic for critical drop alerts only (optional)
        """
        self.ntfy_url = ntfy_url.rstrip('/')
        self.topic = topic
        self.critical_topic = critical_topic
        self.priority = priority

    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert via ntfy.

        Sends to:
        - Main topic (all alerts)
        - Critical topic (only drops, if configured)

        Args:
            alert: Alert object to send

        Returns:
            True if notification sent successfully, False otherwise
        """
        success = True
        is_drop = alert.percentage_change < 0

        # Determine tags and priority based on whether it's a drop or gain
        if is_drop:
            tags = "chart_with_downwards_trend,warning"
            title_prefix = "BUYING OPPORTUNITY"  # Removed emoji from header
        else:
            tags = "chart_with_upwards_trend,white_check_mark"
            title_prefix = "Price Gain"  # Removed emoji from header

        # Build message with threshold information
        message_body = alert.message
        if alert.threshold:
            message_body += f"\n\nAlert Threshold: {alert.threshold}%"

        # Always send to main topic
        try:
            url = f"{self.ntfy_url}/{self.topic}"

            headers = {
                "Title": f"{title_prefix}: {alert.index_name}",
                "Priority": self.priority if is_drop else "default",
                "Tags": tags
            }

            response = requests.post(
                url,
                data=message_body.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            logger.info(f"Alert sent successfully to {url} (main topic)")

        except Exception as e:
            logger.error(f"Failed to send alert to main topic via ntfy: {e}")
            success = False

        # Send to critical topic only if it's a drop AND
        # the drop magnitude meets/exceeds the alert threshold.
        # This ensures 'niftyyy' only gets true buying opportunities.
        if is_drop and self.critical_topic:
            meets_threshold = False
            try:
                if alert.threshold is not None:
                    meets_threshold = abs(alert.percentage_change) >= float(alert.threshold)
            except Exception:
                meets_threshold = False

            if not meets_threshold:
                logger.info(
                    "Skipping critical topic: drop %.2f%% below threshold %.2f%%",
                    abs(alert.percentage_change),
                    alert.threshold if alert.threshold is not None else float('nan')
                )
                return success

            try:
                critical_url = f"{self.ntfy_url}/{self.critical_topic}"

                headers = {
                    "Title": f"CRITICAL: {alert.index_name} Buying Opportunity",  # Removed emoji from header
                    "Priority": "urgent",  # Higher priority for critical drops
                    "Tags": "rotating_light,money_with_wings,chart_with_downwards_trend"
                }

                logger.info(
                    "Sending to critical topic: drop %.2f%% >= threshold %.2f%%",
                    abs(alert.percentage_change),
                    alert.threshold if alert.threshold is not None else float('nan')
                )

                response = requests.post(
                    critical_url,
                    data=message_body.encode('utf-8'),  # Use message_body with threshold
                    headers=headers,
                    timeout=10
                )

                response.raise_for_status()
                logger.info(f"Critical alert sent successfully to {critical_url}")

            except Exception as e:
                logger.error(f"Failed to send critical alert via ntfy: {e}")
                success = False

        return success

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
