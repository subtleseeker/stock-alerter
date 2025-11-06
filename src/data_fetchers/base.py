"""Base class for data fetchers."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from ..models import IndexData


class DataFetcher(ABC):
    """Abstract base class for fetching index data."""

    @abstractmethod
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[IndexData]:
        """
        Fetch historical data for a given symbol.

        Args:
            symbol: Index symbol to fetch
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of IndexData objects
        """
        pass
