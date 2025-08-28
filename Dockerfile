# Minimal Dockerfile for Railway
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip && pip install -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
# Expect env vars provided by Railway dashboard
# BOT_TOKEN, MANAGER_IDS, ADMIN_IDS, DATA_FILE (optional path)
CMD ["python", "main.py"]
