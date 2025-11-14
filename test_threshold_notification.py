"""Test that threshold is included in notifications."""
from datetime import datetime
from src.models import Alert
from src.notifiers import NtfyNotifier

# Create a sample alert with threshold
alert = Alert(
    index_name="TEST INDEX",
    symbol="^TEST",
    current_price=1000.0,
    reference_price=1100.0,
    reference_date=datetime(2025, 11, 10),
    percentage_change=-9.09,  # Drop of 9.09%
    message="TEST INDEX: Dropped 9.09% (from 1100.00 to 1000.00) over 3 day(s) (since 2025-11-10)",
    timestamp=datetime.now(),
    trigger_type="percentage_drop",
    threshold=4.0  # This should appear in the notification
)

# Send notification
notifier = NtfyNotifier(
    ntfy_url="https://ntfy.sh",
    topic="niftyy",
    critical_topic="niftyyy",
    priority="high"
)

print("Sending test alert...")
print(f"Alert message: {alert.message}")
print(f"Alert threshold: {alert.threshold}%")
print(f"Is drop: {alert.percentage_change < 0}")
print()

success = notifier.send_alert(alert)

if success:
    print("✓ Alert sent successfully!")
    print()
    print("Check the notification at: https://ntfy.sh/niftyy")
    print("The notification should include:")
    print(f"  - Main message: {alert.message}")
    print(f"  - Threshold: Alert Threshold: {alert.threshold}%")
    print()
    print("Since this is a drop, it should also be sent to:")
    print("  - Critical topic: https://ntfy.sh/niftyyy")
else:
    print("✗ Failed to send alert")
