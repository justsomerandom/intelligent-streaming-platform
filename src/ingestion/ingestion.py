import os
import subprocess

# Define the list of video sources (webcams, IP cameras)
video_sources = [
    "/dev/video0",  # Local webcam (Linux)
    "/dev/video1",  # Second webcam (Linux)
    "rtsp://your_ip_camera_url"  # IP Camera (Change this)
]

# Base RTSP URL
rtsp_base_url = "rtsp://0.0.0.0:8554/"

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name):
    command = [
        "gst-launch-1.0",
        "v4l2src", f"device={source}",
        "!", "videoconvert",
        "!", "x264enc", "tune=zerolatency",
        "!", "rtph264pay", "pt=96",
        "!", f"rtspclientsink location={rtsp_base_url}{stream_name}"
    ]
    print(f"Starting RTSP stream: {rtsp_base_url}{stream_name}")
    subprocess.Popen(command)

# Start RTSP streams for all sources
for index, source in enumerate(video_sources):
    stream_name = f"camera{index}"
    start_rtsp_stream(source, stream_name)
