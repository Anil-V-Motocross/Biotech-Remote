#!/bin/bash
set -e

echo "----------> Checking for process on port 8000."
PORT=8000

# Kill process on port 8000 if running
if command -v lsof &>/dev/null; then
    PID=$(lsof -t -i:$PORT 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "----------> Killing process $PID running on port $PORT..."
        kill -9 $PID
    fi
fi

# Virtual environment setup
if [ ! -d "venv" ]; then
    echo "----------> Creating venv."
    python3 -m venv venv
else
    echo "----------> venv already exists."
fi

echo "----------> Activating venv."
source ./venv/bin/activate

# Install dependencies
echo "----------> Installing requirements.txt."
pip install -r requirements.txt

echo "----------> Installing gunicorn."
pip install gunicorn

# Django setup
# echo "----------> Running makemigrations."
# python3 manage.py makemigrations

# echo "----------> Running migrate."
# python3 manage.py migrate

# Restart services
echo "----------> Restarting Gunicorn."
nohup /var/lib/jenkins/workspace/git-demo/venv/bin/gunicorn --bind 0.0.0.0:8000 main.wsgi:application > gunicorn.log 2>&1 &

echo "----------> Deployment complete."