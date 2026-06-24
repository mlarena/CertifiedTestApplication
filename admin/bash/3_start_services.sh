#!/bin/bash

# Start CertifiedTestApplication service
SERVICE_NAME="certified-test-application"

echo "Starting $SERVICE_NAME..."
sudo systemctl start "$SERVICE_NAME"
sleep 3
sudo systemctl status "$SERVICE_NAME" --no-pager --lines=10
