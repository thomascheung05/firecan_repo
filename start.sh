#!/bin/bash
cd ~/Thomas/firecan_repo || exit

APP_PID=""
NGROK_PID=""

start_app() {
    echo "[AutoPull] Starting ngrok and app..."
    ./venv/bin/ngrok http 5000 &
    NGROK_PID=$!
    ./venv/bin/python firecan_main.py &
    APP_PID=$!
    echo "[AutoPull] App started (APP_PID=$APP_PID, NGROK_PID=$NGROK_PID)."
}

stop_app() {
    echo "[AutoPull] Stopping app..."
    if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null; then
        kill "$APP_PID"
        wait "$APP_PID" 2>/dev/null
        echo "[AutoPull] App stopped."
    fi
    if [ -n "$NGROK_PID" ] && kill -0 "$NGROK_PID" 2>/dev/null; then
        kill "$NGROK_PID"
        wait "$NGROK_PID" 2>/dev/null
        echo "[AutoPull] Ngrok stopped."
    fi
}

echo "[AutoPull] Started at $(date)"
echo "[AutoPull] Monitoring for new commits every 60s..."
echo

# Start the app for the first time
start_app

while true; do
    git fetch origin >/dev/null 2>&1
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    BRANCH=$(git rev-parse --abbrev-ref HEAD)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[AutoPull] $(date): New update detected on branch $BRANCH. Pulling..."
        stop_app
        git pull origin "$BRANCH"
        echo "[AutoPull] $(date): Pull complete. Restarting app..."
        start_app
    else
        echo "[AutoPull] $(date): No new commits."
    fi

    sleep 60
done

