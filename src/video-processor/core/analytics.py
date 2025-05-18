import cv2
from ultralytics import YOLO
from core.streaming import stream_annotated_frame
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Load the YOLOv5 Tiny model
model = YOLO("yolov5nu.pt")

metrics = {
    "total_frames": 0,
    "total_detections": 0,
    "last_labels": [],
}

# Function to process and annotate frames
async def process_stream(stream_url):
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Failed to connect to {stream_url}")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Stream ended: {stream_url}")
            break

        # Perform object detection
        results = model(frame)
        annotated_frame = results.render()[0]  # Get the annotated frame
        labels = results.names if hasattr(results, "names") else []
        num_detections = len(results.xyxy[0]) if hasattr(results, "xyxy") else 0

        # Update metrics
        metrics["total_frames"] += 1
        metrics["total_detections"] += num_detections
        metrics["last_labels"] = labels

        # Stream the annotated frame using a persistent pipeline (see streaming.py)
        name = f"{stream_url.split('/')[-1]}{frame_count}"
        stream_annotated_frame(annotated_frame, name)
        frame_count += 1

    cap.release()

# FastAPI app for metrics
app = FastAPI()

@app.get("/metrics")
def get_metrics():
    return JSONResponse(content=metrics)