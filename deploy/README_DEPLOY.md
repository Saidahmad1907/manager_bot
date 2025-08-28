# Deployment Guide (Ubuntu VPS, systemd)

## Prerequisites
- Ubuntu 22.04/24.04 VPS with SSH access
- Telegram Bot token
- Your Telegram user ID as manager

## 1) Upload code
Upload this project to the server directory, e.g. `/home/bot/apps/manager_accessory_bot`.

## 2) Install runtime
```
sudo apt update && sudo apt -y install python3-venv python3-pip git
```

## 3) Create venv and install deps
```
cd /home/bot/apps/manager_accessory_bot
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 4) Configure systemd service via helper script
```
chmod +x deploy/install_ubuntu.sh
sudo bash deploy/install_ubuntu.sh bot /home/bot/apps/manager_accessory_bot
```
This creates:
- `/etc/manager-bot.service` (systemd unit)
- `/etc/manager-bot.env` (environment variables)

Edit `/etc/manager-bot.env`:
```
BOT_TOKEN=1234:your-token
MANAGER_IDS=5948727144
ADMIN_IDS=
```
Then restart:
```
sudo systemctl restart manager-bot
journalctl -u manager-bot -f
```

## 5) Update
```
cd /home/bot/apps/manager_accessory_bot
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart manager-bot
```

## Notes
- `data.json` is stored in the app directory. Back it up regularly.
- For security, keep `BOT_TOKEN` out of the code and only in the env file.
- Timezone: `sudo timedatectl set-timezone Asia/Tashkent`.
