import cv2
import torch
import numpy as np
from ultralytics import YOLO

# Load the YOLOv5 Tiny model
model = YOLO("yolov5n.pt")

# List of RTSP streams (from Ingestion)
rtsp_streams = [
    "rtsp://video-ingestion:8554/camera0",
    "rtsp://video-ingestion:8554/camera1",
    "rtsp://video-ingestion:8554/camera2"
]

# Function to process and annotate frames
def process_stream(stream_url):
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Failed to connect to {stream_url}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Stream ended: {stream_url}")
            break

        # Perform object detection
        results = model(frame)
        annotated_frame = results.render()[0]  # Get the annotated frame

        # Send the annotated frame to Streaming (TODO: Add IPC here)
        # (For now, save it locally for testing)
        cv2.imwrite(f"annotated_{stream_url.split('/')[-1]}.jpg", annotated_frame)

    cap.release()

# Process all streams
for stream in rtsp_streams:
    process_stream(stream)
