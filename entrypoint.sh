#!/bin/bash

# Start RTSP server in background
./../usr/local/bin/mediamtx &

# Wait briefly to ensure it's up
sleep 2

# Then run your main Python app
IP_HOST=host.docker.internal IS_LOCAL=false python src/main.py
