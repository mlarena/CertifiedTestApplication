#!/bin/bash

# Full installer for CertifiedTestApplication
# Run as root: sudo bash install.sh [--port <port>]

set -e

APP_NAME="CertifiedTestApplication"
USER_NAME="cta"
INSTALL_DIR="/opt/cta"
SERVICE_NAME="certified-test-application"
DEFAULT_PORT="5002"

# Parse command line arguments for port
APP_PORT="$DEFAULT_PORT"
while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            APP_PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--port <port_number>]"
            exit 1
            ;;
    esac
done

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo $0 [--port <port>]"
    exit 1
fi

echo "=================================================="
echo " CertifiedTestApplication Installer"
echo " Port: $APP_PORT"
echo "=================================================="
echo ""

# === STEP 1: Check dependencies ===
echo "=== [1/4] Checking dependencies ==="

check_package() {
    PACKAGE=$1
    if command -v "$PACKAGE" >/dev/null 2>&1; then
        echo "  $PACKAGE is already installed."
    else
        echo "  Installing $PACKAGE..."
        apt-get update -qq
        apt-get install -y "$PACKAGE" -qq
    fi
}

check_package "sudo"
check_package "unzip"
check_package "curl"
check_package "rsync"
check_package "gnupg2"

echo "Dependencies OK."
echo ""

# === STEP 2: Setup PostgreSQL ===
echo "=== [2/4] Setting up PostgreSQL ==="

if command -v psql >/dev/null 2>&1; then
    echo "  PostgreSQL already installed."
else
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg --yes
    apt-get update -qq
    apt-get install -y postgresql-18 postgresql-client-18 postgresql-contrib-18 -qq
    systemctl start postgresql@18-main
    systemctl enable postgresql@18-main
fi

sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '12345678';" >/dev/null 2>&1
echo "PostgreSQL ready."
echo ""

# === STEP 3: Install application ===
echo "=== [3/4] Installing application ==="

if ! getent group "$USER_NAME" &>/dev/null; then
    groupadd --system "$USER_NAME"
    echo "  Created group: $USER_NAME"
fi

if ! id "$USER_NAME" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin \
            --gid "$USER_NAME" "$USER_NAME"
    echo "  Created user: $USER_NAME"
fi

mkdir -p "$INSTALL_DIR"
chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

if [ ! -f "$APP_NAME.zip" ]; then
    echo "Error: $APP_NAME.zip not found in current directory."
    exit 1
fi

echo "  Unpacking $APP_NAME.zip..."
unzip -o "$APP_NAME.zip" -d "$INSTALL_DIR"

if [ -f "$INSTALL_DIR/json.zip" ]; then
    echo "  Unpacking json.zip..."
    mkdir -p "$INSTALL_DIR/json"
    unzip -o "$INSTALL_DIR/json.zip" -d "$INSTALL_DIR/json"
fi

chmod -R +x "$INSTALL_DIR"
chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

echo "Application installed."
echo ""

# === STEP 4: Create service ===
echo "=== [4/4] Creating service ==="

APP_EXEC="$INSTALL_DIR/$APP_NAME"

if [ ! -f "$APP_EXEC" ]; then
    echo "Error: Application not found at $APP_EXEC"
    exit 1
fi

chmod +x "$APP_EXEC"

cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Certified Test Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR
ExecStart=$APP_EXEC --urls http://*:$APP_PORT
Restart=always
RestartSec=10
TimeoutStartSec=60
TimeoutStopSec=30
KillSignal=SIGINT
Environment=ASPNETCORE_ENVIRONMENT=Production
Environment=DOTNET_PRINT_TELEMETRY_MESSAGE=false
SyslogIdentifier=$SERVICE_NAME
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME

echo "  Starting service..."
systemctl restart $SERVICE_NAME
sleep 3

echo ""
echo "=================================================="
echo " Installation complete!"
echo "=================================================="
echo ""
echo " Service status:"
systemctl status $SERVICE_NAME --no-pager --lines=5
echo ""
echo " Management commands:"
echo "   Start:    sudo systemctl start $SERVICE_NAME"
echo "   Stop:     sudo systemctl stop $SERVICE_NAME"
echo "   Restart:  sudo systemctl restart $SERVICE_NAME"
echo "   Status:   sudo systemctl status $SERVICE_NAME"
echo "   Logs:     sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo " Access: http://$(hostname -I | awk '{print $1}'):$APP_PORT"
