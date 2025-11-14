"""Test which sectoral indices are available via Yahoo Finance."""
import yfinance as yf
from datetime import datetime, timedelta

# Mapping from chanakya-live repo
SECTORAL_INDICES = {
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY FINANCIAL SERVICES": "NIFTY_FIN_SERVICE",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY IT": "^CNXIT",
    "NIFTY MEDIA": "^CNXMEDIA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY PSU BANK": "^CNXPSUBANK",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY HEALTHCARE": "NIFTY_HEALTHCARE",
    "NIFTY CONSUMER DURABLES": "NIFTY_CONSR_DURBL",
    "NIFTY OIL & GAS": "NIFTY_OIL_AND_GAS",
}

def test_index(name, symbol):
    """Test if an index symbol works with Yahoo Finance."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)

        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            return False, "No data returned"

        return True, f"✓ Got {len(data)} days of data, Latest close: {data['Close'].iloc[-1]:.2f}"

    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == "__main__":
    print("Testing Sectoral Indices with Yahoo Finance")
    print("=" * 70)

    working = []
    not_working = []

    for name, symbol in SECTORAL_INDICES.items():
        print(f"\nTesting {name} ({symbol})...")
        success, message = test_index(name, symbol)

        if success:
            print(f"  ✓ {message}")
            working.append((name, symbol))
        else:
            print(f"  ✗ {message}")
            not_working.append((name, symbol))

    print("\n" + "=" * 70)
    print(f"\nSUMMARY:")
    print(f"Working: {len(working)}/{len(SECTORAL_INDICES)}")
    print(f"Not working: {len(not_working)}/{len(SECTORAL_INDICES)}")

    if working:
        print("\n✓ WORKING INDICES:")
        for name, symbol in working:
            print(f"  - {name}: {symbol}")

    if not_working:
        print("\n✗ NOT WORKING INDICES:")
        for name, symbol in not_working:
            print(f"  - {name}: {symbol}")
