"""
Find optimal alert thresholds for each index to generate 5-10 buying opportunity alerts per year.

This script:
1. Fetches 5 years of historical data
2. Simulates our alert logic (7-day lookback)
3. Tests various threshold levels
4. Finds thresholds that yield 5-10 alerts per year
"""
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# All indices we're tracking
INDICES = {
    "NIFTY 500": "^CRSLDX",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY ENERGY": "^CNXENERGY",
}

# Target: 5-10 alerts per year
TARGET_MIN_ALERTS = 5
TARGET_MAX_ALERTS = 10

# Test thresholds from 1.0% to 10.0% in 0.5% increments
TEST_THRESHOLDS = [round(x * 0.5, 1) for x in range(2, 21)]  # [1.0, 1.5, 2.0, ..., 10.0]


def fetch_historical_data(symbol, name, years=5):
    """Fetch historical data for analysis."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        print(f"  Fetching {years} years of data for {name}...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            print(f"  ❌ No data returned for {name}")
            return None

        print(f"  ✓ Got {len(data)} days of data ({data.index[0].date()} to {data.index[-1].date()})")
        return data

    except Exception as e:
        print(f"  ❌ Error fetching {name}: {e}")
        return None


def simulate_alerts(data, threshold_pct):
    """
    Simulate our alert logic with a given threshold.

    Returns: Number of alerts that would have been triggered.

    Logic:
    - For each day (starting from day 8 onwards)
    - Check if today's close dropped more than threshold% from ANY of the previous 7 days
    - If yes, count as an alert (and skip next 7 days to avoid duplicate alerts)
    """
    if len(data) < 8:
        return 0

    alerts = []
    i = 7  # Start from day 8 (index 7)

    while i < len(data):
        current_price = data['Close'].iloc[i]
        current_date = data.index[i]

        # Check against previous 7 days
        max_drop_pct = 0
        max_drop_date = None

        for lookback in range(1, 8):
            prev_price = data['Close'].iloc[i - lookback]
            prev_date = data.index[i - lookback]

            # Calculate percentage change (negative = drop)
            pct_change = ((current_price - prev_price) / prev_price) * 100

            # Track maximum drop
            if pct_change < max_drop_pct:
                max_drop_pct = pct_change
                max_drop_date = prev_date

        # If drop exceeds threshold (remember, it's negative)
        if max_drop_pct <= -threshold_pct:
            alerts.append({
                'date': current_date,
                'drop_pct': abs(max_drop_pct),
                'from_date': max_drop_date
            })
            # Skip next 7 days to avoid duplicate alerts for same dip
            i += 7
        else:
            i += 1

    return len(alerts), alerts


def find_optimal_threshold(data, name):
    """Find threshold that yields 5-10 alerts per year."""

    if data is None or len(data) < 365:
        return None

    # Calculate number of years of data
    days_of_data = len(data)
    years_of_data = days_of_data / 252  # Approximate trading days per year

    print(f"\n  Analyzing {name}:")
    print(f"  Data span: {years_of_data:.1f} years ({days_of_data} days)")
    print(f"  Target: {TARGET_MIN_ALERTS}-{TARGET_MAX_ALERTS} alerts/year")
    print(f"\n  {'Threshold':<12} {'Total Alerts':<15} {'Alerts/Year':<15} {'Status'}")
    print(f"  {'-'*60}")

    results = []

    for threshold in TEST_THRESHOLDS:
        alert_count, alert_details = simulate_alerts(data, threshold)
        alerts_per_year = alert_count / years_of_data if years_of_data > 0 else 0

        status = ""
        if TARGET_MIN_ALERTS <= alerts_per_year <= TARGET_MAX_ALERTS:
            status = "✓ TARGET RANGE"
        elif alerts_per_year < TARGET_MIN_ALERTS:
            status = "Too few"
        else:
            status = "Too many"

        print(f"  {threshold:>10.1f}%  {alert_count:>13}  {alerts_per_year:>13.1f}  {status}")

        results.append({
            'threshold': threshold,
            'total_alerts': alert_count,
            'alerts_per_year': alerts_per_year,
            'in_target': TARGET_MIN_ALERTS <= alerts_per_year <= TARGET_MAX_ALERTS,
            'details': alert_details
        })

    # Find thresholds in target range
    in_range = [r for r in results if r['in_target']]

    if in_range:
        # Pick the middle threshold from the valid range
        optimal = in_range[len(in_range) // 2]
        print(f"\n  ✓ OPTIMAL THRESHOLD: {optimal['threshold']:.1f}%")
        print(f"    → Would generate {optimal['alerts_per_year']:.1f} alerts/year")
        return optimal
    else:
        # Find closest
        closest = min(results, key=lambda x: abs(x['alerts_per_year'] - ((TARGET_MIN_ALERTS + TARGET_MAX_ALERTS) / 2)))
        print(f"\n  ⚠ No exact match found. Closest: {closest['threshold']:.1f}%")
        print(f"    → Would generate {closest['alerts_per_year']:.1f} alerts/year")
        return closest


def main():
    print("=" * 80)
    print("FINDING OPTIMAL ALERT THRESHOLDS FOR BUYING OPPORTUNITIES")
    print("=" * 80)
    print(f"\nGoal: Find thresholds that generate {TARGET_MIN_ALERTS}-{TARGET_MAX_ALERTS} alerts per year")
    print("Strategy: Buy on dips when index drops X% from any of last 7 days\n")

    all_results = {}

    for name, symbol in INDICES.items():
        print(f"\n{'='*80}")
        print(f"ANALYZING: {name} ({symbol})")
        print(f"{'='*80}")

        data = fetch_historical_data(symbol, name, years=5)

        if data is not None:
            optimal = find_optimal_threshold(data, name)
            all_results[name] = {
                'symbol': symbol,
                'optimal': optimal,
                'data_years': len(data) / 252
            }

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY - OPTIMAL THRESHOLDS")
    print("=" * 80)
    print(f"\n{'Index':<20} {'Symbol':<15} {'Threshold':<12} {'Alerts/Year':<15}")
    print("-" * 80)

    for name, result in all_results.items():
        if result['optimal']:
            print(f"{name:<20} {result['symbol']:<15} {result['optimal']['threshold']:>10.1f}% "
                  f"{result['optimal']['alerts_per_year']:>13.1f}")

    # Generate config
    print("\n" + "=" * 80)
    print("RECOMMENDED CONFIG FOR config.yaml")
    print("=" * 80)

    for name, result in all_results.items():
        if result['optimal']:
            opt = result['optimal']
            print(f"""
  - symbol: "{result['symbol']}"
    name: "{name}"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: {opt['threshold']:.1f}  # {opt['alerts_per_year']:.1f} alerts/year (based on {result['data_years']:.1f} years of data)
""")

    # Print example alerts
    print("\n" + "=" * 80)
    print("EXAMPLE HISTORICAL ALERTS (Last 12 months)")
    print("=" * 80)

    for name, result in all_results.items():
        if result['optimal'] and result['optimal']['details']:
            print(f"\n{name}:")
            recent_alerts = [a for a in result['optimal']['details']
                           if a['date'] >= datetime.now() - timedelta(days=365)]

            if recent_alerts:
                for alert in recent_alerts[-5:]:  # Show last 5
                    print(f"  {alert['date'].date()}: Drop of {alert['drop_pct']:.2f}% "
                          f"(from {alert['from_date'].date()})")
            else:
                print("  No alerts in last 12 months")


if __name__ == "__main__":
    main()
