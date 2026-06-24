#!/bin/bash

# Stop CertifiedTestApplication service
SERVICE_NAME="certified-test-application"

echo "Stopping $SERVICE_NAME..."
sudo systemctl stop "$SERVICE_NAME"
echo "✅ $SERVICE_NAME stopped."
