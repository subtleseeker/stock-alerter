#!/usr/bin/env python3
"""Debug script to test NSE India data fetcher."""

import logging
from datetime import datetime, timedelta
from src.data_fetchers.nse_india import NSEIndiaDataFetcher

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_nse_fetcher():
    """Test NSE India data fetcher with debug output."""
    fetcher = NSEIndiaDataFetcher()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=12)

    print(f"\n{'='*60}")
    print(f"Testing NSE India Data Fetcher")
    print(f"Symbol: ^NSEI")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"{'='*60}\n")

    try:
        data = fetcher.fetch_historical_data('^NSEI', start_date, end_date)

        print(f"\n{'='*60}")
        print(f"Results:")
        print(f"{'='*60}")
        print(f"Number of data points: {len(data)}")

        if data:
            print(f"\nFirst data point:")
            print(f"  Date: {data[0].date}")
            print(f"  Open: {data[0].open}")
            print(f"  High: {data[0].high}")
            print(f"  Low: {data[0].low}")
            print(f"  Close: {data[0].close}")
            print(f"  Volume: {data[0].volume}")

            print(f"\nLast data point:")
            print(f"  Date: {data[-1].date}")
            print(f"  Open: {data[-1].open}")
            print(f"  High: {data[-1].high}")
            print(f"  Low: {data[-1].low}")
            print(f"  Close: {data[-1].close}")
            print(f"  Volume: {data[-1].volume}")
        else:
            print("No data returned")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR:")
        print(f"{'='*60}")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_nse_fetcher()
