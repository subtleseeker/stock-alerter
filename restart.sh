#!/bin/bash
# Restart the NIFTY alerter service with latest code changes

echo "Restarting NIFTY alerter service..."
docker compose restart nifty-alerter

echo "Tailing logs (Ctrl+C to exit)..."
docker compose logs -f nifty-alerter
