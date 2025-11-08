"""NSE India data fetcher implementation."""
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .base import DataFetcher
from ..models import IndexData

logger = logging.getLogger(__name__)


class NSEIndiaDataFetcher(DataFetcher):
    """Fetch index data from NSE India."""

    # Symbol mapping from common names to NSE index names
    SYMBOL_MAP = {
        '^NSEI': 'NIFTY 50',
        '^NSEBANK': 'NIFTY BANK',
        '^CNXIT': 'NIFTY IT',
    }

    def __init__(self):
        """Initialize NSE India fetcher."""
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session with NSE India to get cookies."""
        try:
            self.session.get(
                self.base_url,
                headers=self.headers,
                timeout=10
            )
            logger.info("NSE India session initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize NSE session: {e}")

    def _get_index_name(self, symbol: str) -> str:
        """Convert symbol to NSE index name."""
        return self.SYMBOL_MAP.get(symbol, symbol)

    def _fetch_current_data(self, index_name: str) -> Optional[Dict]:
        """
        Fetch current index data from NSE.

        Args:
            index_name: NSE index name (e.g., 'NIFTY 50')

        Returns:
            Dictionary with current index data or None
        """
        try:
            # Use allIndices endpoint which gives cleaner index data
            url = f"{self.base_url}/api/allIndices"

            response = self.session.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f"Failed to parse JSON from NSE: {e}")
                    logger.debug(f"Response text: {response.text[:200]}")
                    return None

                # Find the specific index in the data
                if 'data' in data:
                    for item in data['data']:
                        if item.get('index') == index_name or item.get('indexSymbol') == index_name:
                            logger.info(f"Found NSE data for {index_name}")
                            return item

                logger.warning(f"Index {index_name} not found in NSE data")
            else:
                logger.warning(f"Failed to fetch NSE data for {index_name}: status {response.status_code}")

            return None

        except Exception as e:
            logger.error(f"Error fetching NSE data: {e}", exc_info=True)
            return None

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[IndexData]:
        """
        Fetch historical data from NSE India.

        Note: NSE India API provides limited historical data through their public API.
        This implementation fetches current data multiple times to build a history.
        For actual historical data, Yahoo Finance should be used as primary source.

        Args:
            symbol: Index symbol (e.g., ^NSEI for NIFTY 50)
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of IndexData objects
        """
        try:
            logger.info(f"Fetching NSE data for {symbol}")

            index_name = self._get_index_name(symbol)
            current_data = self._fetch_current_data(index_name)

            if not current_data:
                logger.warning(f"No current data available from NSE for {symbol}")
                return []

            # Create IndexData from current data
            # NSE provides: last, previousClose, open, high, low
            index_data_list = []

            # Add today's data
            if 'last' in current_data:
                today = IndexData(
                    symbol=symbol,
                    date=datetime.now(),
                    close=float(current_data['last']),
                    open=float(current_data.get('open', current_data['last'])),
                    high=float(current_data.get('high', current_data['last'])),
                    low=float(current_data.get('low', current_data['last'])),
                    volume=None
                )
                index_data_list.append(today)

            # Add yesterday's data if available
            if 'previousClose' in current_data:
                yesterday = IndexData(
                    symbol=symbol,
                    date=datetime.now() - timedelta(days=1),
                    close=float(current_data['previousClose']),
                    open=float(current_data['previousClose']),
                    high=float(current_data['previousClose']),
                    low=float(current_data['previousClose']),
                    volume=None
                )
                index_data_list.append(yesterday)

            logger.info(f"Fetched {len(index_data_list)} data points from NSE for {symbol}")
            return index_data_list

        except Exception as e:
            logger.error(f"Error fetching NSE data for {symbol}: {e}")
            raise
