"""Base class for notifiers."""
from abc import ABC, abstractmethod
from ..models import Alert


class Notifier(ABC):
    """Abstract base class for sending notifications."""

    @abstractmethod
    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert notification.

        Args:
            alert: Alert object to send

        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
