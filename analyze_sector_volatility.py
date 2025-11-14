"""Analyze volatility of sectoral indices to determine appropriate alert thresholds."""
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# 7 Core sectoral indices
SECTORS = {
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY ENERGY": "^CNXENERGY",
}

def analyze_volatility(symbol, name, period_days=180):
    """Analyze volatility metrics for an index."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            return None

        # Calculate daily returns
        data['Daily_Return'] = data['Close'].pct_change() * 100

        # Calculate volatility metrics
        std_dev = data['Daily_Return'].std()
        mean_return = data['Daily_Return'].mean()

        # Calculate maximum single-day drops and gains
        max_drop = data['Daily_Return'].min()
        max_gain = data['Daily_Return'].max()

        # Calculate 7-day rolling max change (similar to our alert logic)
        rolling_max_change = []
        for i in range(7, len(data)):
            current_price = data['Close'].iloc[i]
            lookback_prices = data['Close'].iloc[i-7:i]
            max_change = max(abs((current_price - p) / p * 100) for p in lookback_prices)
            rolling_max_change.append(max_change)

        avg_7day_max_change = sum(rolling_max_change) / len(rolling_max_change) if rolling_max_change else 0
        percentile_95_7day = sorted(rolling_max_change)[int(len(rolling_max_change) * 0.95)] if rolling_max_change else 0

        return {
            'name': name,
            'symbol': symbol,
            'daily_volatility': std_dev,
            'mean_daily_return': mean_return,
            'max_single_day_drop': max_drop,
            'max_single_day_gain': max_gain,
            'avg_7day_max_change': avg_7day_max_change,
            'percentile_95_7day_change': percentile_95_7day,
            'data_points': len(data)
        }

    except Exception as e:
        print(f"Error analyzing {name}: {e}")
        return None

def suggest_threshold(metrics):
    """Suggest alert threshold based on volatility metrics."""
    if not metrics:
        return 2.0  # Default

    # Use 7-day max change as primary indicator
    # We want to alert when change is meaningful but not too frequent
    # Using 70% of 95th percentile as threshold
    suggested = metrics['percentile_95_7day_change'] * 0.7

    # Round to nearest 0.5
    suggested = round(suggested * 2) / 2

    # Clamp between 1.5% and 5.0%
    suggested = max(1.5, min(5.0, suggested))

    return suggested

if __name__ == "__main__":
    print("Analyzing Sectoral Index Volatility (Last 6 Months)")
    print("=" * 90)

    results = []

    for name, symbol in SECTORS.items():
        print(f"\nAnalyzing {name} ({symbol})...")
        metrics = analyze_volatility(symbol, name)

        if metrics:
            threshold = suggest_threshold(metrics)
            metrics['suggested_threshold'] = threshold
            results.append(metrics)

            print(f"  Daily Volatility: {metrics['daily_volatility']:.2f}%")
            print(f"  Max Single Day Drop: {metrics['max_single_day_drop']:.2f}%")
            print(f"  Avg 7-Day Max Change: {metrics['avg_7day_max_change']:.2f}%")
            print(f"  95th Percentile 7-Day Change: {metrics['percentile_95_7day_change']:.2f}%")
            print(f"  → Suggested Threshold: {threshold:.1f}%")

    # Sort by volatility
    results.sort(key=lambda x: x['daily_volatility'], reverse=True)

    print("\n" + "=" * 90)
    print("\nSUMMARY - Sorted by Volatility (High to Low)")
    print("-" * 90)
    print(f"{'Sector':<25} {'Daily Vol':<12} {'Avg 7D Chg':<15} {'Suggested Threshold':<20}")
    print("-" * 90)

    for r in results:
        print(f"{r['name']:<25} {r['daily_volatility']:>10.2f}% {r['avg_7day_max_change']:>13.2f}% {r['suggested_threshold']:>18.1f}%")

    print("\n" + "=" * 90)
    print("\nRECOMMENDED CONFIG:")
    print("-" * 90)

    for r in results:
        print(f"""
  - symbol: "{r['symbol']}"
    name: "{r['name']}"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: {r['suggested_threshold']:.1f}  # {r['daily_volatility']:.2f}% daily volatility
""")
