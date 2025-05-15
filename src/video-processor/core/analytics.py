import cv2
import subprocess
from threading import Event
from ultralytics import YOLO
from streaming import stream_annotated_frame

# Load the YOLOv5 Tiny model
model = YOLO("yolov5nu.pt")

# Function to process and annotate frames
async def process_stream(stream_url):
    global url_lock, url_unlock
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Failed to connect to {stream_url}")
        return

    frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Stream ended: {stream_url}")
            break

        # Perform object detection
        results = model(frame)
        annotated_frame = results.render()[0]  # Get the annotated frame

        # Stream the annotated frame using a persistent pipeline (see streaming.py)
        name = f"{stream_url.split('/')[-1]}{frame}"
        stream_annotated_frame(annotated_frame, name)
        frame += 1

    cap.release()