import subprocess

# Define input streams (raw and annotated)
streams = {
    "raw_camera0": "rtsp://video-ingestion:8554/camera0",
    "annotated_camera0": "rtsp://video-analytics:8555/annotated_camera0"
}

# Start streaming each stream
for name, url in streams.items():
    command = [
        "gst-launch-1.0",
        "rtspsrc", f"location={url}",
        "!", "rtph264depay", 
        "!", "h264parse",
        "!", "rtph264pay", "pt=96",
        "!", f"rtspclientsink location=rtsp://0.0.0.0:8556/{name}"
    ]
    print(f"Starting Streaming for {name} at rtsp://0.0.0.0:8556/{name}")
    subprocess.Popen(command)
