# Quick Start Guide

Get the NIFTY Alerter Service running in under 5 minutes!

## Step 1: Start the Services

```bash
docker-compose up -d
```

This will:
- Pull and start the ntfy notification server
- Build and start the NIFTY alerter service
- Create a network for the services to communicate

## Step 2: Check the Logs

```bash
docker-compose logs -f nifty-alerter
```

You should see:
- Service starting up
- Fetching NIFTY 500 data
- Running the initial alert check
- Scheduling daily checks at 4 PM IST

## Step 3: Subscribe to Notifications

### Option A: Web Browser
1. Open `http://localhost:8080` in your browser
2. In the topic field, enter: `nifty-alerts`
3. Click "Subscribe"
4. You'll now receive alerts in your browser!

### Option B: Mobile App
1. Install the ntfy app:
   - iOS: [App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
2. Open the app
3. Add your server: `http://YOUR_SERVER_IP:8080`
4. Subscribe to topic: `nifty-alerts`

### Option C: Command Line
```bash
# Subscribe and listen for alerts
curl -s http://localhost:8080/nifty-alerts/json
```

## Step 4: Test the Notification

Send a test notification to verify everything works:

```bash
curl -d "Test Alert: NIFTY Alerter is working!" http://localhost:8080/nifty-alerts
```

## What Happens Next?

- The service runs continuously in the background
- Every day at **4:00 PM IST**, it:
  1. Fetches the latest NIFTY 500 data
  2. Checks if today's close has dropped >2% from any of the last 6 days
  3. Sends an alert if triggered
- On startup, it runs an immediate check (for testing)

## Viewing Status

```bash
# Check if services are running
docker-compose ps

# View all logs
docker-compose logs

# View only alerter logs
docker-compose logs nifty-alerter

# View only ntfy logs
docker-compose logs ntfy
```

## Stopping the Service

```bash
# Stop but keep data
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Common Use Cases

### Change Alert Time
Edit `config/config.yaml`:
```yaml
alert_service:
  check_time: "15:30"  # Change to 3:30 PM
```

Then restart:
```bash
docker-compose restart nifty-alerter
```

### Add Another Index (e.g., NIFTY 50)
Edit `config/config.yaml`:
```yaml
indices:
  - symbol: "^CRSLDX"
    name: "NIFTY 500"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: 2.0

  - symbol: "^NSEI"  # Add this
    name: "NIFTY 50"
    lookback_days: 7
    alert_triggers:
      - type: "percentage_drop"
        threshold: 1.5
```

Restart:
```bash
docker-compose restart nifty-alerter
```

### Change Alert Threshold
Edit `config/config.yaml` and change threshold from `2.0` to any percentage:
```yaml
alert_triggers:
  - type: "percentage_drop"
    threshold: 3.0  # Now triggers on 3% drops
```

## Troubleshooting

### Ports Already in Use
If port 8080 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8081:80"  # Use 8081 instead
```

### Services Won't Start
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### No Data Being Fetched
- Ensure you have internet connectivity
- Yahoo Finance might be temporarily unavailable
- Check logs: `docker-compose logs nifty-alerter`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize alert triggers in `config/config.yaml`
- Set up mobile notifications with the ntfy app
- Add your own indices or create custom triggers

## Getting Help

- Check logs: `docker-compose logs`
- Review configuration: `cat config/config.yaml`
- See architecture: Check README.md

Happy monitoring! 📈📉
