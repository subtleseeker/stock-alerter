"""NSE India data fetcher implementation"""
import logging
from curl_cffi import requests
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .base import DataFetcher
from ..models import IndexData

logger = logging.getLogger(__name__)


class NSEIndiaDataFetcher(DataFetcher):
    """Fetch index data from NSE India using production-grade approach."""

    # Symbol mapping from common names to NSE index names
    SYMBOL_MAP = {
        '^NSEI': 'NIFTY 50',
        '^NSEBANK': 'NIFTY BANK',
        '^CNXIT': 'NIFTY IT',
    }

    def __init__(self):
        """Initialize NSE India fetcher with production-grade headers."""
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session with NSE India to get cookies - production approach."""
        try:
            # Visit homepage first to get cookies
            self.session.headers.update(self.headers)
            self.session.get(self.base_url, timeout=20, impersonate="chrome120")

            # Sometimes visiting market data pages helps get all cookies
            time.sleep(1)
            self.session.get(f"{self.base_url}/market-data/live-equity-market", timeout=20, impersonate="chrome120")

            logger.info("NSE India session initialized with cookies")
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
                timeout=10,
                impersonate="chrome120"
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

    def _fetch_historical_index_data(self, index_name: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch historical index OHLC data from NSE

        Args:
            index_name: NSE index name (e.g., 'NIFTY 50')
            start_date: Start date
            end_date: End date

        Returns:
            List of dictionaries containing OHLC data
        """
        try:
            # Format dates as DD-MM-YYYY (NSE format)
            formatted_start = start_date.strftime("%d-%m-%Y")
            formatted_end = end_date.strftime("%d-%m-%Y")

            # Encode index name for URL
            encoded_index = urllib.parse.quote(index_name)

            # Use the historical indices API
            url = f"{self.base_url}/api/historical/indicesHistory?indexType={encoded_index}&from={formatted_start}&to={formatted_end}"

            logger.info(f"Fetching historical data from NSE: {index_name} ({formatted_start} to {formatted_end})")

            # Small delay before request to avoid rate limiting
            time.sleep(0.5)

            response = self.session.get(url, timeout=20, impersonate="chrome120")
            response.raise_for_status()

            data = response.json()

            # NSE API returns data in a nested structure
            # data -> data -> indexCloseOnlineRecords (list of OHLC records)
            data_dict = data.get("data", {})
            if isinstance(data_dict, dict):
                historical_data = data_dict.get("indexCloseOnlineRecords", [])
            else:
                historical_data = []

            logger.debug(f"Retrieved {len(historical_data)} records from NSE")
            return historical_data

        except Exception as e:
            logger.error(f"Error fetching historical data from NSE: {e}")
            return []

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[IndexData]:
        """
        Fetch historical data from NSE India using production-grade API.

        Uses the historical indices API which provides proper OHLC data.

        Args:
            symbol: Index symbol (e.g., ^NSEI for NIFTY 50)
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of IndexData objects
        """
        try:
            logger.info(f"Fetching NSE historical data for {symbol}")

            index_name = self._get_index_name(symbol)
            historical_data = self._fetch_historical_index_data(index_name, start_date, end_date)

            if not historical_data:
                logger.warning(f"No historical data available from NSE for {symbol}")
                return []

            # Convert NSE data format to IndexData objects
            # NSE API format uses: EOD_TIMESTAMP, EOD_OPEN_INDEX_VAL, EOD_HIGH_INDEX_VAL, EOD_LOW_INDEX_VAL, EOD_CLOSE_INDEX_VAL
            index_data_list = []
            for item in historical_data:
                try:
                    index_data = IndexData(
                        symbol=symbol,
                        date=datetime.strptime(item['EOD_TIMESTAMP'], '%d-%b-%Y'),
                        close=float(item['EOD_CLOSE_INDEX_VAL']),
                        open=float(item['EOD_OPEN_INDEX_VAL']),
                        high=float(item['EOD_HIGH_INDEX_VAL']),
                        low=float(item['EOD_LOW_INDEX_VAL']),
                        volume=None  # NSE historical indices API doesn't provide volume for indices
                    )
                    index_data_list.append(index_data)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid data point: {e}")
                    continue

            # Sort by date (oldest first)
            index_data_list.sort(key=lambda x: x.date)

            logger.info(f"Fetched {len(index_data_list)} data points from NSE for {symbol}")
            return index_data_list

        except Exception as e:
            logger.error(f"Error fetching NSE data for {symbol}: {e}")
            raise
