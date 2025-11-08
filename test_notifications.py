#!/usr/bin/env python3
"""Test script to verify notification functionality."""
import sys
import os
from datetime import datetime, timedelta

# Add src to path and set up package
sys.path.insert(0, os.path.dirname(__file__))

from src.models import IndexData, Alert
from src.notifiers.ntfy_notifier import NtfyNotifier

def test_notifications():
    """Test all notification types."""

    # Initialize notifier (will use environment variables or defaults)
    ntfy_url = os.getenv('NTFY_URL', 'https://ntfy.sh')
    ntfy_topic = os.getenv('NTFY_TOPIC', 'niftyy')

    notifier = NtfyNotifier(
        ntfy_url=ntfy_url,
        topic=ntfy_topic,
        priority='high'
    )

    print(f"Testing notifications to {ntfy_url}/{ntfy_topic}\n")

    # Test 1: Alert notification
    print("Test 1: Sending alert notification...")
    test_alert = Alert(
        index_name="NIFTY 500",
        symbol="^CRSLDX",
        current_price=23450.50,
        reference_price=24000.00,
        reference_date=datetime.now() - timedelta(days=1),
        percentage_change=-2.29,
        message="NIFTY 500 dropped -2.29% from yesterday (₹24000.00 → ₹23450.50)",
        timestamp=datetime.now(),
        trigger_type="percentage_drop"
    )

    result = notifier.send_alert(test_alert)
    print(f"✓ Alert sent: {result}\n")

    # Test 2: Status notification (no alerts)
    print("Test 2: Sending status notification (all clear)...")
    status_message = """Daily Index Check - No Alerts

NIFTY 500: ↑ +0.75% (₹24180.00)
NIFTY 50: ↑ +1.20% (₹19850.00)"""

    result = notifier.send_status(
        title="NIFTY Alerter - All Clear",
        message=status_message
    )
    print(f"✓ Status sent: {result}\n")

    # Test 3: Error notification
    print("Test 3: Sending error notification...")
    result = notifier.send_error(
        title="Error: NIFTY 500",
        message="Error fetching data for NIFTY 500: Connection timeout after 10s"
    )
    print(f"✓ Error sent: {result}\n")

    # Test 4: Critical error notification
    print("Test 4: Sending critical error notification...")
    result = notifier.send_error(
        title="NIFTY Alerter - Critical Error",
        message="Alert check failed with error:\nDivision by zero in percentage calculation"
    )
    print(f"✓ Critical error sent: {result}\n")

    print("=" * 60)
    print("All notification tests completed!")
    print(f"Check your ntfy topic: {ntfy_url}/{ntfy_topic}")
    print("=" * 60)

if __name__ == "__main__":
    test_notifications()
