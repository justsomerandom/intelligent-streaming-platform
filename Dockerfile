FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 libgl1-mesa-glx \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (YOLOv5 + FastAPI + OpenCV)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code
COPY ./src /app/src

# Expose ports
EXPOSE 8000
EXPOSE 8554
EXPOSE 8556

# Command to run the Analytics Service
CMD ["python3", "/app/src/main.py"]
