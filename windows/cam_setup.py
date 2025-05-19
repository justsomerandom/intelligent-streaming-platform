import cv2
import threading
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import uvicorn
import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

app = FastAPI()

# Global map of index → VideoCapture object
video_sources = {}
locks = {}

def get_frame_stream(index):
    cap = video_sources.get(index)
    lock = locks.get(index)
    if cap is None or not cap.isOpened():
        return
    while True:
        with lock:
            success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.get("/cam{index}.mjpg")
async def video_feed(index: int):
    if index not in video_sources:
        return Response(status_code=404, content="Camera not available")
    return StreamingResponse(get_frame_stream(index),
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
def root():
    return {
        "message": "Available camera streams",
        "streams": [f"/cam{i}.mjpg" for i in video_sources.keys()]
    }

@app.get("/cams")
def list_cams():
    return {
        "cameras": [f"/cam{i}.mjpg" for i in video_sources.keys()]
    }

def open_all_webcams(max_devices=5):
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"✔️  Camera {i} is available.")
            video_sources[i] = cap
            locks[i] = threading.Lock()
        else:
            print(f"❌  Camera {i} does not exist, proceeding...")
            cap.release()
            break

if __name__ == "__main__":
    open_all_webcams()
    uvicorn.run(app, host="0.0.0.0", port=8081)
