"""Percentage drop alert trigger."""
import logging
from datetime import datetime
from typing import List, Optional
from .base import AlertTrigger
from ..models import IndexData, Alert

logger = logging.getLogger(__name__)


class PercentageDropTrigger(AlertTrigger):
    """Trigger alert when price drops by a certain percentage from any previous day."""

    def __init__(self, threshold_percentage: float):
        """
        Initialize the percentage drop trigger.

        Args:
            threshold_percentage: Percentage threshold (e.g., 2.0 for 2%)
        """
        self.threshold_percentage = threshold_percentage

    def check_trigger(
        self,
        index_name: str,
        data: List[IndexData]
    ) -> Optional[Alert]:
        """
        ALWAYS send notification with the maximum percentage change over the lookback period.

        Finds the largest change (positive or negative) compared to any previous day
        and sends a notification with that information.

        Args:
            index_name: Name of the index
            data: List of IndexData objects (sorted by date, oldest first)

        Returns:
            Alert object with maximum percentage change (always returned if data available)
        """
        if len(data) < 2:
            logger.warning(f"Not enough data for {index_name}, need at least 2 days")
            return None

        # Sort data by date (oldest first) to ensure correct order
        sorted_data = sorted(data, key=lambda x: x.date)

        # Today's data is the last element
        today = sorted_data[-1]
        today_close = today.close

        # Find the maximum percentage change (most negative = largest drop)
        max_change = None
        max_change_day = None
        max_change_days_ago = 0

        # Check against each previous day to find maximum change
        for i in range(len(sorted_data) - 2, -1, -1):
            reference_day = sorted_data[i]
            reference_close = reference_day.close

            # Calculate percentage change
            # Negative value means drop, positive means gain
            pct_change = ((today_close - reference_close) / reference_close) * 100

            days_ago = len(sorted_data) - 1 - i

            logger.info(
                f"{index_name}: Today's close ({today_close:.2f}) vs "
                f"{days_ago} day(s) ago ({reference_close:.2f}): "
                f"{pct_change:+.2f}%"
            )

            # Track the maximum absolute change
            if max_change is None or abs(pct_change) > abs(max_change):
                max_change = pct_change
                max_change_day = reference_day
                max_change_days_ago = days_ago

        # Always send notification with maximum change
        if max_change is not None:
            if max_change < 0:
                # It's a drop
                message = (
                    f"{index_name}: Dropped {abs(max_change):.2f}% "
                    f"(from {max_change_day.close:.2f} to {today_close:.2f}) "
                    f"over {max_change_days_ago} day(s) "
                    f"(since {max_change_day.date.strftime('%Y-%m-%d')})"
                )
            else:
                # It's a gain
                message = (
                    f"{index_name}: Gained {abs(max_change):.2f}% "
                    f"(from {max_change_day.close:.2f} to {today_close:.2f}) "
                    f"over {max_change_days_ago} day(s) "
                    f"(since {max_change_day.date.strftime('%Y-%m-%d')})"
                )

            logger.info(f"Maximum change: {message}")

            return Alert(
                index_name=index_name,
                symbol=today.symbol,
                current_price=today_close,
                reference_price=max_change_day.close,
                reference_date=max_change_day.date,
                percentage_change=max_change,
                message=message,
                timestamp=datetime.now(),
                trigger_type="percentage_drop",
                threshold=self.threshold_percentage
            )

        logger.info(f"{index_name}: No data available for comparison")
        return None
