FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 libgl1-mesa-glx wget \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install rtsp-simple-server
RUN wget https://github.com/bluenviron/mediamtx/releases/download/v1.12.2/mediamtx_v1.12.2_darwin_amd64.tar.gz \
    && tar -xzf mediamtx_v1.12.2_darwin_amd64.tar.gz \
    && mv mediamtx /usr/local/bin/ \
    && rm mediamtx_v1.12.2_darwin_amd64.tar.gz \
    && chmod +x /usr/local/bin/mediamtx

# Install Python dependencies (YOLOv5 + FastAPI + OpenCV)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code
COPY ./src /app/src

# Expose ports
EXPOSE 8080

# Command to run
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
