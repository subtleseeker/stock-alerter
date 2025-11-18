#!/bin/bash
# Rebuild and restart the NIFTY alerter service with latest code changes

set -e

echo "Rebuilding and restarting NIFTY alerter service..."
docker compose up -d --build nifty-alerter

echo "Verifying critical-topic threshold gating in running container..."
if docker compose exec -T nifty-alerter grep -n "Skipping critical topic" /app/src/notifiers/ntfy_notifier.py > /dev/null; then
  echo "✓ Gating detected in notifier (critical topic will only get ≥ threshold drops)."
else
  echo "✗ Gating code not found in container. Check volume mounts or rebuild compose stack."
fi

echo "Tailing logs (Ctrl+C to exit)..."
docker compose logs -f nifty-alerter
