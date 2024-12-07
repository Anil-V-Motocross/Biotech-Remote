#!/bin/bash

# Port to kill
PORT=8000

# Find the process ID (PID) using the port
PID=$(sudo lsof -t -i:$PORT)

# Check if PID exists
if [ -n "$PID" ]; then
    echo "----------> Killing process $PID running on port $PORT..."
    sudo kill -9 $PID
    echo "----------> Process killed successfully."
else
    echo "----------> No process is running on port $PORT."
fi

echo "----------> Activating venv."
python3 -m venv venv
source ./venv/bin/activate
echo "----------> venv activated sucessfully."

echo "----------> Installing requirements.txt."
pip install -r requirements.txt
echo "----------> requirements.txt installed successfully."

echo "----------> Installing gunicorn."
pip install gunicorn
echo "----------> gunicorn installed sucessfuuly."

echo "----------> Executing makemigrations."
python3 manage.py makemigrations
echo "----------> makemigrations executed successfully."

echo "----------> Executing migrate."
python3 manage.py migrate
echo "----------> migrate executed successfully."

# echo "----------> Starting server on port 8000."
# /var/lib/jenkins/workspace/git-demo/venv/bin/gunicorn --bind 0.0.0.0:8000 main.wsgi:application
# echo "----------> Running server on port 8000."

echo "----------> restarting server."
systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl restart gunicorn.service
echo "----------> server restarted successfully."
