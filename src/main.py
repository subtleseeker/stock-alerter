"""Main application entry point."""
import os
import logging
import schedule
import time
from pathlib import Path
from .config import Settings, load_config
from .alert_service import AlertService
from .data_fetchers import FallbackDataFetcher
from .notifiers import NtfyNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Main application function."""
    logger.info("Starting NIFTY Alerter Service")

    # Load settings
    settings = Settings()
    logger.info(f"Loaded settings: check_time={settings.alert_check_time}, timezone={settings.timezone}")

    # Load configuration
    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    config = load_config(config_path)

    # Initialize components with fallback data fetcher
    data_fetcher = FallbackDataFetcher()
    notifier = NtfyNotifier(
        ntfy_url=settings.ntfy_url,
        topic=settings.ntfy_topic,
        priority=config.get('ntfy', {}).get('priority', 'high')
    )

    # Create service
    alert_service = AlertService(
        data_fetcher=data_fetcher,
        notifier=notifier
    )

    # Define the job
    def job():
        """Job to run alert check."""
        try:
            alert_service.run_check(config)
        except Exception as e:
            logger.error(f"Error during alert check: {e}", exc_info=True)
            # Send error notification
            try:
                notifier.send_error(
                    title="NIFTY Alerter - Critical Error",
                    message=f"Alert check failed with error:\n{str(e)}"
                )
            except Exception as notify_error:
                logger.error(f"Failed to send error notification: {notify_error}")

    # Schedule the job
    check_time = config.get('alert_service', {}).get('check_time', settings.alert_check_time)
    schedule.every().day.at(check_time).do(job)

    logger.info(f"Scheduled daily check at {check_time}")
    logger.info("Service is running. Press Ctrl+C to stop.")

    # Run immediately on startup for testing
    logger.info("Running initial check on startup...")
    job()

    # Keep the service running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Service stopped by user")


if __name__ == "__main__":
    main()
