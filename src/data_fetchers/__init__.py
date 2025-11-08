"""Data fetchers package."""
from .base import DataFetcher
from .yahoo_finance import YahooFinanceDataFetcher
from .nse_india import NSEIndiaDataFetcher
from .fallback_fetcher import FallbackDataFetcher

__all__ = [
    "DataFetcher",
    "YahooFinanceDataFetcher",
    "NSEIndiaDataFetcher",
    "FallbackDataFetcher"
]
