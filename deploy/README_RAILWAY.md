# Deploy to Railway (Simple PaaS)

## 1) Create a Railway project
- Go to https://railway.app, sign in with GitHub.
- Click "New Project" → "Deploy from GitHub repo" → select your repo containing this project.

## 2) Configure service
- Railway auto-detects the Dockerfile and builds the image.
- In Variables, add:
  - `BOT_TOKEN` = your Telegram token
  - `MANAGER_IDS` = e.g., `5948727144`
  - `ADMIN_IDS` = (optional)
  - `DATA_FILE` = `/data/data.json` (recommended)

## 3) Persistence (recommended)
- Add a Volume in Railway UI, mount path: `/data` (1GB is enough for JSON).
- Ensure `DATA_FILE=/data/data.json` is set so data survives restarts.

## 4) Deploy
- Click Deploy. Logs will show aiogram polling started.

## 5) Update
- Push changes to GitHub → Railway rebuilds and redeploys automatically.

Troubleshooting
- If bot doesn't respond, check logs and verify `BOT_TOKEN` is valid.
- Make sure the service is running as a worker (no HTTP required for long polling).
