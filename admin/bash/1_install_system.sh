#!/bin/bash

# First-time system setup for CertifiedTestApplication
# Run as root: sudo bash 1_install_system.sh

set -e

APP_NAME="CertifiedTestApplication"
USER_NAME="cta"
INSTALL_DIR="/opt/cta"
SERVICE_NAME="certified-test-application"
DEFAULT_PORT="5002"

echo "=== Installing $APP_NAME ==="

# Create user and group
if ! getent group "$USER_NAME" &>/dev/null; then
    groupadd --system "$USER_NAME"
    echo "Created group: $USER_NAME"
fi

if ! id "$USER_NAME" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin \
            --gid "$USER_NAME" "$USER_NAME"
    echo "Created user: $USER_NAME"
fi

# Create install directory
mkdir -p "$INSTALL_DIR"
chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"
echo "Created directory: $INSTALL_DIR"

# Check if zip is present
if [ ! -f "$APP_NAME.zip" ]; then
    echo "Error: $APP_NAME.zip not found in current directory."
    echo "Please copy the deployment bundle to this server first."
    exit 1
fi

# Unpack application
echo "Unpacking $APP_NAME.zip..."
unzip -o "$APP_NAME.zip" -d "$INSTALL_DIR"

# Set permissions
chmod +x "$INSTALL_DIR/$APP_NAME"
chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

# Verify
echo "File info:"
file "$INSTALL_DIR/$APP_NAME"

echo ""
echo "✅ Installation complete."
echo "Next step: Create the service with: sudo bash create-service.sh --port $DEFAULT_PORT"
