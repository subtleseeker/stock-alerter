"""Base class for alert triggers."""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import IndexData, Alert


class AlertTrigger(ABC):
    """Abstract base class for alert triggers."""

    @abstractmethod
    def check_trigger(
        self,
        index_name: str,
        data: List[IndexData]
    ) -> Optional[Alert]:
        """
        Check if alert should be triggered based on index data.

        Args:
            index_name: Name of the index
            data: List of IndexData objects (sorted by date, oldest first)

        Returns:
            Alert object if triggered, None otherwise
        """
        pass
