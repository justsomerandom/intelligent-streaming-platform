#!/bin/bash

# Start RTSP server in background
rtsp-simple-server &

# Wait briefly to ensure it's up
sleep 2

# Then run your main Python app
python main.py
