#!/bin/bash

# Update CertifiedTestApplication (preserves appsettings.json)
# Run as root: sudo bash 2_update_system.sh

set -e

APP_NAME="CertifiedTestApplication"
USER_NAME="cta"
INSTALL_DIR="/opt/cta"
SERVICE_NAME="certified-test-application"

echo "=== Updating $APP_NAME ==="

# Check if zip is present
if [ ! -f "$APP_NAME.zip" ]; then
    echo "Error: $APP_NAME.zip not found in current directory."
    exit 1
fi

# Stop service if running
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping $SERVICE_NAME..."
    systemctl stop "$SERVICE_NAME"
fi

# Extract to temp
TMP_EXTRACT="/tmp/cta_update"
rm -rf "$TMP_EXTRACT"
mkdir -p "$TMP_EXTRACT"

echo "Extracting $APP_NAME.zip..."
unzip -o "$APP_NAME.zip" -d "$TMP_EXTRACT"

# Sync files, preserving config
echo "Syncing files (preserving appsettings.json)..."
rsync -av --delete \
    --exclude='appsettings.json' \
    --exclude='appsettings.*.json' \
    "$TMP_EXTRACT/" "$INSTALL_DIR/"

# Set permissions for all files
chmod -R +x "$INSTALL_DIR"
chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

# Cleanup
rm -rf "$TMP_EXTRACT"

echo "✅ Update complete."
echo "Start service: sudo systemctl start $SERVICE_NAME"
