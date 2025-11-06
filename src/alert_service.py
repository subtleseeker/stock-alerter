"""Main alert service."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .models import Alert
from .data_fetchers import DataFetcher, YahooFinanceDataFetcher
from .alert_triggers import AlertTrigger, PercentageDropTrigger
from .notifiers import Notifier, NtfyNotifier

logger = logging.getLogger(__name__)


class AlertService:
    """Main service for checking alerts."""

    def __init__(
        self,
        data_fetcher: DataFetcher,
        notifier: Notifier
    ):
        """
        Initialize alert service.

        Args:
            data_fetcher: Data fetcher instance
            notifier: Notifier instance
        """
        self.data_fetcher = data_fetcher
        self.notifier = notifier

    def check_index(
        self,
        index_config: Dict[str, Any]
    ) -> List[Alert]:
        """
        Check a single index for alerts.

        Args:
            index_config: Index configuration dictionary

        Returns:
            List of triggered alerts
        """
        symbol = index_config['symbol']
        name = index_config['name']
        lookback_days = index_config.get('lookback_days', 7)

        logger.info(f"Checking {name} ({symbol})")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 5)  # Add buffer for weekends

        # Fetch data
        try:
            data = self.data_fetcher.fetch_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )

            if not data:
                logger.warning(f"No data fetched for {name}")
                return []

            # Limit to lookback_days + 1 (today)
            if len(data) > lookback_days + 1:
                data = data[-(lookback_days + 1):]

            logger.info(f"Fetched {len(data)} days of data for {name}")

        except Exception as e:
            logger.error(f"Error fetching data for {name}: {e}")
            return []

        # Check each trigger
        alerts = []
        for trigger_config in index_config.get('alert_triggers', []):
            trigger_type = trigger_config['type']

            # Create appropriate trigger
            if trigger_type == 'percentage_drop':
                threshold = trigger_config.get('threshold', 2.0)
                trigger = PercentageDropTrigger(threshold_percentage=threshold)
            else:
                logger.warning(f"Unknown trigger type: {trigger_type}")
                continue

            # Check trigger
            alert = trigger.check_trigger(name, data)
            if alert:
                alerts.append(alert)

        return alerts

    def run_check(self, config: Dict[str, Any]) -> None:
        """
        Run alert check for all configured indices.

        Args:
            config: Application configuration
        """
        logger.info("=" * 60)
        logger.info("Starting alert check")
        logger.info("=" * 60)

        all_alerts = []

        for index_config in config.get('indices', []):
            alerts = self.check_index(index_config)
            all_alerts.extend(alerts)

        # Send alerts
        if all_alerts:
            logger.info(f"Found {len(all_alerts)} alert(s), sending notifications...")
            for alert in all_alerts:
                self.notifier.send_alert(alert)
        else:
            logger.info("No alerts triggered")

        logger.info("=" * 60)
        logger.info("Alert check completed")
        logger.info("=" * 60)
