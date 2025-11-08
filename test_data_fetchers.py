#!/usr/bin/env python3
"""Test script to verify all data fetchers work."""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from src.data_fetchers import (
    YahooFinanceDataFetcher,
    NSEIndiaDataFetcher,
    FallbackDataFetcher
)

def test_yahoo_finance():
    """Test Yahoo Finance data fetcher."""
    print("=" * 60)
    print("Testing Yahoo Finance Data Fetcher")
    print("=" * 60)

    fetcher = YahooFinanceDataFetcher()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)

    try:
        data = fetcher.fetch_historical_data(
            symbol="^NSEI",
            start_date=start_date,
            end_date=end_date
        )

        if data:
            print(f"✓ Yahoo Finance: Got {len(data)} data points")
            print(f"  Latest: {data[-1].date.strftime('%Y-%m-%d')} - Close: ₹{data[-1].close:.2f}")
            return True
        else:
            print("✗ Yahoo Finance: No data returned")
            return False
    except Exception as e:
        print(f"✗ Yahoo Finance failed: {e}")
        return False


def test_nse_india():
    """Test NSE India data fetcher."""
    print("\n" + "=" * 60)
    print("Testing NSE India Data Fetcher")
    print("=" * 60)

    fetcher = NSEIndiaDataFetcher()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)

    try:
        data = fetcher.fetch_historical_data(
            symbol="^NSEI",
            start_date=start_date,
            end_date=end_date
        )

        if data:
            print(f"✓ NSE India: Got {len(data)} data points")
            for item in data:
                print(f"  {item.date.strftime('%Y-%m-%d')} - Close: ₹{item.close:.2f}")
            return True
        else:
            print("✗ NSE India: No data returned")
            return False
    except Exception as e:
        print(f"✗ NSE India failed: {e}")
        return False


def test_fallback():
    """Test Fallback data fetcher."""
    print("\n" + "=" * 60)
    print("Testing Fallback Data Fetcher")
    print("=" * 60)

    fetcher = FallbackDataFetcher()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)

    try:
        data = fetcher.fetch_historical_data(
            symbol="^NSEI",
            start_date=start_date,
            end_date=end_date
        )

        if data:
            print(f"✓ Fallback Fetcher: Got {len(data)} data points")
            print(f"  Latest: {data[-1].date.strftime('%Y-%m-%d')} - Close: ₹{data[-1].close:.2f}")
            return True
        else:
            print("✗ Fallback Fetcher: No data returned")
            return False
    except Exception as e:
        print(f"✗ Fallback Fetcher failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\nTesting All Data Fetchers")
    print("=" * 60)

    results = {
        'Yahoo Finance': test_yahoo_finance(),
        'NSE India': test_nse_india(),
        'Fallback': test_fallback()
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    working_count = 0
    for name, success in results.items():
        status = "✓ WORKING" if success else "✗ FAILED"
        print(f"{name:20} : {status}")
        if success:
            working_count += 1

    print("=" * 60)
    print(f"Working data sources: {working_count}/3")

    if working_count >= 2:
        print("✓ SUCCESS: At least 2 data sources are working!")
    else:
        print("⚠ WARNING: Less than 2 data sources are working")

    print("=" * 60)


if __name__ == "__main__":
    main()
