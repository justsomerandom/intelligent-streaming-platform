from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import requests

app = FastAPI()

# In-memory store for active streams
streams = {
    "raw": {},
    "annotated": {}
}

# Model for stream configuration
class StreamConfig(BaseModel):
    source: str
    type: str  # raw or annotated
    resolution: str = "640x480"
    framerate: int = 30
    bitrate: str = "1M"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Intelligent Multi-Source Video Platform API"}

@app.get("/streams")
def list_streams():
    return streams

@app.post("/streams/start")
def start_stream(config: StreamConfig):
    if config.type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")

    stream_name = f"{config.type}_camera_{len(streams[config.type])}"

    # Command for GStreamer (raw stream for simplicity)
    if config.type == "raw":
        command = [
            "gst-launch-1.0",
            "v4l2src", f"device={config.source}",
            "!", "videoconvert",
            "!", f"video/x-raw,width={config.resolution.split('x')[0]},height={config.resolution.split('x')[1]},framerate={config.framerate}/1",
            "!", "x264enc", "tune=zerolatency", f"bitrate={config.bitrate}",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location=rtsp://video-streaming:8556/{stream_name}"
        ]
        subprocess.Popen(command)
        streams[config.type][stream_name] = {
            "source": config.source,
            "resolution": config.resolution,
            "framerate": config.framerate,
            "bitrate": config.bitrate,
            "status": "active"
        }
        return {"message": f"Started {config.type} stream at rtsp://video-streaming:8556/{stream_name}"}

@app.post("/streams/stop")
def stop_stream(stream_name: str, stream_type: str):
    if stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")

    if stream_name not in streams[stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Stopping stream (for now, we will just mark it inactive)
    streams[stream_type][stream_name]["status"] = "inactive"
    return {"message": f"Stopped {stream_type} stream {stream_name}"}

@app.get("/streams/status")
def stream_status():
    return streams
