import cv2
import subprocess
from threading import Event
from ultralytics import YOLO

# Initialize a variable to control streaming access
url_lock = None
url_unlock = Event()

# Load the YOLOv5 Tiny model
model = YOLO("yolov5n.pt")

# Base RTSP URL
rtsp_base_url = "rtsp://0.0.0.0:8554/"

# Function to process and annotate frames
async def process_stream(stream_url):
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Failed to connect to {stream_url}")
        return

    first_frame = True
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Stream ended: {stream_url}")
            break

        # Perform object detection
        results = model(frame)
        annotated_frame = results.render()[0]  # Get the annotated frame

        # Stream the annotated frame
        url = f"{rtsp_base_url}{stream_url.split('/')[-1]}"
        command = [
            "gst-launch-1.0",
            "appsrc",
            "!", "videoconvert",
            "!", "x264enc", "tune=zerolatency",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location={url}"
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        if first_frame:
            url_lock = url
            url_unlock.set()
        process.stdin.write(annotated_frame.tobytes())
        process.stdin.close()
        process.wait()

    cap.release()

def lock():
    global url_lock
    if url_lock is not None:
        url_lock = None
    if url_unlock.is_set():
        url_unlock.clear()