"""Fallback data fetcher with multiple sources."""
import logging
from datetime import datetime
from typing import List
from .base import DataFetcher
from .yahoo_finance import YahooFinanceDataFetcher
from .nse_india import NSEIndiaDataFetcher
from ..models import IndexData

logger = logging.getLogger(__name__)


class FallbackDataFetcher(DataFetcher):
    """
    Data fetcher that tries multiple sources with fallback logic.

    Tries sources in order:
    1. Yahoo Finance (best for historical data)
    2. NSE India (fallback for current data)
    """

    def __init__(self):
        """Initialize fallback fetcher with multiple data sources."""
        self.fetchers = [
            ('Yahoo Finance', YahooFinanceDataFetcher()),
            ('NSE India', NSEIndiaDataFetcher()),
        ]
        logger.info(f"Initialized FallbackDataFetcher with {len(self.fetchers)} sources")

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[IndexData]:
        """
        Fetch historical data trying multiple sources.

        Args:
            symbol: Index symbol
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of IndexData objects

        Raises:
            Exception: If all data sources fail
        """
        errors = []

        for source_name, fetcher in self.fetchers:
            try:
                logger.info(f"Trying {source_name} for {symbol}...")
                data = fetcher.fetch_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )

                if data:
                    logger.info(f"✓ Successfully fetched {len(data)} data points from {source_name}")
                    return data
                else:
                    error_msg = f"{source_name} returned empty data"
                    logger.warning(error_msg)
                    errors.append(error_msg)

            except Exception as e:
                error_msg = f"{source_name} failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)

        # All sources failed
        error_summary = f"All data sources failed for {symbol}: " + "; ".join(errors)
        logger.error(error_summary)
        raise Exception(error_summary)
