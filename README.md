# NIFTY Alerter Service

A dockerized service that monitors NIFTY 500 index data and generates alerts when significant price drops occur.

## Features

- **Extensible Architecture**: Easy to add new indices, triggers, or notification methods
- **Daily Monitoring**: Automatically checks alerts at 4 PM IST
- **Self-hosted Notifications**: Uses ntfy for push notifications
- **Historical Analysis**: Compares today's close against the last 7 days
- **Docker-based**: Easy deployment with docker-compose

## Alert Logic

The service triggers an alert if today's closing price has dropped more than 2% compared to ANY of the previous 6 days:

- Today's close vs 1 day ago < -2%
- OR Today's close vs 2 days ago < -2%
- OR Today's close vs 3 days ago < -2%
- ... and so on

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Internet connection to fetch market data

### Setup

1. **Clone or navigate to the repository**:
   ```bash
   cd /path/to/nifty-alerter
   ```

2. **Configure environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f nifty-alerter
   ```

5. **Access ntfy web interface**:
   - Open browser: `http://localhost:8080`
   - Subscribe to topic: `nifty-alerts`

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
alert_service:
  check_time: "16:00"  # 4 PM IST
  timezone: "Asia/Kolkata"

indices:
  - symbol: "^CRSLDX"  # NIFTY 500
    name: "NIFTY 500"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: 2.0

ntfy:
  url: "http://ntfy:80"
  topic: "nifty-alerts"
  priority: "high"
```

### Environment Variables (`.env`)

```bash
NTFY_URL=http://ntfy:80
NTFY_TOPIC=nifty-alerts
TZ=Asia/Kolkata
ALERT_CHECK_TIME=16:00
```

## Extending the Service

### Adding New Indices

Edit `config/config.yaml`:

```yaml
indices:
  - symbol: "^CRSLDX"
    name: "NIFTY 500"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: 2.0

  - symbol: "^NSEI"  # NIFTY 50
    name: "NIFTY 50"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: 1.5
```

### Adding New Trigger Types

1. Create a new trigger class in `src/alert_triggers/`:

```python
from .base import AlertTrigger
from ..models import IndexData, Alert

class MyCustomTrigger(AlertTrigger):
    def check_trigger(self, index_name: str, data: List[IndexData]) -> Optional[Alert]:
        # Implement your custom logic
        pass
```

2. Register it in `src/alert_triggers/__init__.py`

3. Use it in `config/config.yaml`:

```yaml
alert_triggers:
  - type: "my_custom_trigger"
    param1: value1
```

### Adding New Data Sources

1. Create a new fetcher in `src/data_fetchers/`:

```python
from .base import DataFetcher

class MyDataFetcher(DataFetcher):
    def fetch_historical_data(self, symbol, start_date, end_date):
        # Implement your data fetching logic
        pass
```

2. Update `src/main.py` to use your fetcher

### Adding New Notification Methods

1. Create a new notifier in `src/notifiers/`:

```python
from .base import Notifier

class MyNotifier(Notifier):
    def send_alert(self, alert: Alert) -> bool:
        # Implement your notification logic
        pass
```

2. Update `src/main.py` to use your notifier

## Service Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Alerter only
docker-compose logs -f nifty-alerter

# Ntfy only
docker-compose logs -f ntfy
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

## Receiving Notifications

### Web Interface
1. Open `http://localhost:8080` in your browser
2. Subscribe to the topic `nifty-alerts`
3. You'll receive alerts in real-time

### Mobile App
1. Install ntfy app from App Store or Google Play
2. Add your server: `http://your-server-ip:8080`
3. Subscribe to topic: `nifty-alerts`

### CLI
```bash
# Subscribe to alerts
curl -s http://localhost:8080/nifty-alerts/json

# Test notification
curl -d "Test alert" http://localhost:8080/nifty-alerts
```

## Architecture

```
┌─────────────────────────────────────────┐
│         AlertService (Main)              │
│  - Orchestrates the alert checking       │
│  - Runs on schedule (daily at 4 PM)      │
└──────────┬──────────────────────┬────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌────────────────────┐
│  DataFetcher     │   │   Notifier         │
│  - YahooFinance  │   │   - NtfyNotifier   │
└──────────────────┘   └────────────────────┘
           │
           ▼
┌──────────────────────┐
│   AlertTrigger       │
│   - PercentageDrop   │
└──────────────────────┘
```

## Data Sources

The service uses Yahoo Finance to fetch NIFTY 500 data:
- Symbol: `^CRSLDX` (NIFTY 500 index)
- Data includes: Open, High, Low, Close, Volume
- Historical data for the last 7+ days

## Troubleshooting

### Service Not Starting
```bash
# Check logs
docker-compose logs

# Check if ports are available
netstat -an | grep 8080
```

### No Alerts Received
1. Check if market is open (alerts only trigger on trading days)
2. Verify data is being fetched: `docker-compose logs nifty-alerter`
3. Test ntfy: `curl -d "Test" http://localhost:8080/nifty-alerts`

### Time Zone Issues
Ensure `TZ=Asia/Kolkata` is set in docker-compose.yml

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
