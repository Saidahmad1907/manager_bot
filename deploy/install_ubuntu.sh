#!/usr/bin/env bash
set -euo pipefail

# Quick installer for Ubuntu 22.04+/24.04
# Usage: curl -fsSL https://example.com/install_ubuntu.sh | bash -s -- <BOT_USER> <APP_DIR>
# Example: ... | bash -s -- bot /home/bot/apps/manager_accessory_bot

BOT_USER=${1:-bot}
APP_DIR=${2:-/home/${BOT_USER}/apps/manager_accessory_bot}
SERVICE_NAME=${3:-manager-bot}

sudo apt update
sudo apt -y install python3-venv python3-pip git

# Create user if missing
if ! id -u "$BOT_USER" >/dev/null 2>&1; then
  sudo adduser --disabled-password --gecos "" "$BOT_USER"
fi
sudo mkdir -p "$(dirname "$APP_DIR")"
sudo chown -R "$BOT_USER":"$BOT_USER" "$(dirname "$APP_DIR")"

sudo -iu "$BOT_USER" bash <<EOS
set -e
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Expect code uploaded here before running this script.
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
EOS

# Create env file
sudo tee /etc/${SERVICE_NAME}.env >/dev/null <<'ENV'
# Fill values then: sudo systemctl restart manager-bot
BOT_TOKEN=
MANAGER_IDS=
ADMIN_IDS=
ENV

# Create systemd unit
sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null <<UNIT
[Unit]
Description=Manager Accessory Telegram Bot (aiogram)
After=network-online.target
Wants=network-online.target

[Service]
User=${BOT_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=/etc/${SERVICE_NAME}.env
Environment=PYTHONUNBUFFERED=1
ExecStart=${APP_DIR}/.venv/bin/python ${APP_DIR}/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now ${SERVICE_NAME}
sudo systemctl status ${SERVICE_NAME} --no-pager -l
