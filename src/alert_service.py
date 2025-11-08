"""Main alert service."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .models import Alert
from .data_fetchers import DataFetcher, YahooFinanceDataFetcher
from .alert_triggers import AlertTrigger, PercentageDropTrigger
from .notifiers import Notifier, NtfyNotifier

logger = logging.getLogger(__name__)


class IndexCheckResult:
    """Result of checking an index."""
    def __init__(self, index_name: str, symbol: str):
        self.index_name = index_name
        self.symbol = symbol
        self.alerts: List[Alert] = []
        self.error: Optional[str] = None
        self.current_price: Optional[float] = None
        self.previous_price: Optional[float] = None
        self.percentage_change: Optional[float] = None
        self.has_data = False


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
    ) -> IndexCheckResult:
        """
        Check a single index for alerts.

        Args:
            index_config: Index configuration dictionary

        Returns:
            IndexCheckResult containing alerts, errors, and status info
        """
        symbol = index_config['symbol']
        name = index_config['name']
        lookback_days = index_config.get('lookback_days', 7)

        result = IndexCheckResult(name, symbol)

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
                result.error = f"No data available for {name} ({symbol})"
                return result

            # Limit to lookback_days + 1 (today)
            if len(data) > lookback_days + 1:
                data = data[-(lookback_days + 1):]

            logger.info(f"Fetched {len(data)} days of data for {name}")
            result.has_data = True

            # Store current and previous price info
            if len(data) >= 2:
                result.current_price = data[-1].close
                result.previous_price = data[-2].close
                result.percentage_change = ((result.current_price - result.previous_price) / result.previous_price) * 100

        except Exception as e:
            logger.error(f"Error fetching data for {name}: {e}")
            result.error = f"Error fetching data for {name}: {str(e)}"
            return result

        # Check each trigger
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
                result.alerts.append(alert)

        return result

    def run_check(self, config: Dict[str, Any]) -> None:
        """
        Run alert check for all configured indices.

        Args:
            config: Application configuration
        """
        logger.info("=" * 60)
        logger.info("Starting alert check")
        logger.info("=" * 60)

        results = []
        all_alerts = []
        errors = []

        # Check all indices
        for index_config in config.get('indices', []):
            result = self.check_index(index_config)
            results.append(result)

            if result.error:
                errors.append(result)

            all_alerts.extend(result.alerts)

        # Send error notifications
        if errors:
            logger.warning(f"Found {len(errors)} error(s) during index checks")
            for error_result in errors:
                self.notifier.send_error(
                    title=f"Error: {error_result.index_name}",
                    message=error_result.error
                )

        # Send alerts
        if all_alerts:
            logger.info(f"Found {len(all_alerts)} alert(s), sending notifications...")
            for alert in all_alerts:
                self.notifier.send_alert(alert)
        else:
            # No alerts triggered - send status message
            logger.info("No alerts triggered")

            # Build status message
            status_lines = ["Daily Index Check - No Alerts", ""]

            for result in results:
                if result.has_data and result.percentage_change is not None:
                    direction = "↑" if result.percentage_change >= 0 else "↓"
                    status_lines.append(
                        f"{result.index_name}: {direction} {result.percentage_change:+.2f}% "
                        f"(₹{result.current_price:.2f})"
                    )

            if status_lines:
                self.notifier.send_status(
                    title="NIFTY Alerter - All Clear",
                    message="\n".join(status_lines)
                )

        logger.info("=" * 60)
        logger.info("Alert check completed")
        logger.info("=" * 60)
