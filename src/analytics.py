import cv2
from ultralytics import YOLO
from streaming import stream_annotated_frame

# Load the YOLOv5 Tiny model
model = YOLO("yolov5nu.pt")

metrics = {
    "total_frames": 0,
    "total_detections": 0,
    "last_labels": [],
}

# Function to process and annotate frames
def process_stream(stream_url):
    print(f"Processing stream: {stream_url}")
    cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
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
        results = model(frame, verbose=False)
        result = results[0]
        annotated_frame = result.plot()

        labels = result.names if hasattr(result, "names") else []
        num_detections = len(result.boxes) if hasattr(result, "boxes") else 0

        # Update metrics
        metrics["total_frames"] += 1
        metrics["total_detections"] += num_detections
        metrics["last_labels"] = labels

        # Stream the annotated frame using a persistent pipeline (see streaming.py)
        name = f"annotated_{stream_url.split('/')[-1]}"
        stream_annotated_frame(annotated_frame, name)
        frame_count += 1

    cap.release()

def get_metrics():
    return metrics