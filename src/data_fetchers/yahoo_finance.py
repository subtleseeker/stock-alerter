"""Yahoo Finance data fetcher implementation."""
import logging
from datetime import datetime
from typing import List
import yfinance as yf
from .base import DataFetcher
from ..models import IndexData

logger = logging.getLogger(__name__)


class YahooFinanceDataFetcher(DataFetcher):
    """Fetch index data from Yahoo Finance."""

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[IndexData]:
        """
        Fetch historical data from Yahoo Finance.

        Args:
            symbol: Index symbol (e.g., ^CRSLDX for NIFTY 500)
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of IndexData objects
        """
        try:
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return []

            index_data_list = []
            for date, row in df.iterrows():
                index_data = IndexData(
                    symbol=symbol,
                    date=date.to_pydatetime(),
                    close=float(row['Close']),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    volume=int(row['Volume']) if 'Volume' in row else None
                )
                index_data_list.append(index_data)

            logger.info(f"Fetched {len(index_data_list)} data points for {symbol}")
            return index_data_list

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
