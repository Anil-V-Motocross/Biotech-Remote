#!/bin/bash
# set -e

# PORT=8000

# # Kill process on port
# echo "----------> Checking for process on port $PORT."
# if command -v lsof &>/dev/null; then
#     PID=$(sudo lsof -t -i:$PORT)
# elif command -v fuser &>/dev/null; then
#     PID=$(sudo fuser $PORT/tcp 2>/dev/null)
# else
#     echo "----------> Neither lsof nor fuser is available. Exiting."
#     exit 1
# fi

# if [ -n "$PID" ]; then
#     echo "----------> Killing process $PID running on port $PORT..."
#     sudo kill -9 $PID
#     echo "----------> Process killed successfully."
# else
#     echo "----------> No process running on port $PORT."
# fi

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
echo "----------> Restarting Gunicorn and Nginx."
sudo systemctl restart gunicorn.service
sudo systemctl restart nginx

echo "----------> Deployment complete."
