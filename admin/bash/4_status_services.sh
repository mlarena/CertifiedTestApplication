#!/bin/bash

# Check status of CertifiedTestApplication service
SERVICE_NAME="certified-test-application"

echo "=== $SERVICE_NAME Status ==="
sudo systemctl status "$SERVICE_NAME" --no-pager --lines=10
