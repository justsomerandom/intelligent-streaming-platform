from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import analytics
from typing import Optional

app = FastAPI()

# In-memory store for active streams and analytics
streams = {
    "raw": {},
    "annotated": {}
}
analytics_metrics = {}

class StreamConfig(BaseModel):
    source: str
    type: str  # "raw" or "annotated"
    resolution: str = "640x480"
    framerate: int = 30
    bitrate: str = "1M"

class StreamUpdate(BaseModel):
    stream_name: str
    stream_type: str  # "raw" or "annotated"
    resolution: Optional[str] = None
    framerate: Optional[int] = None
    bitrate: Optional[str] = None

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

    if config.type == "raw":
        command = [
            "gst-launch-1.0",
            "v4l2src", f"device={config.source}",
            "!", "videoconvert",
            "!", f"video/x-raw,width={config.resolution.split('x')[0]},height={config.resolution.split('x')[1]},framerate={config.framerate}/1",
            "!", "x264enc", "tune=zerolatency", f"bitrate={config.bitrate}",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location=rtsp://video-processor:8556/{stream_name}"
        ]
        subprocess.Popen(command)
    else:
        command = [
            "gst-launch-1.0",
            "v4l2src", f"device={config.source}",
            "!", "videoconvert",
            "!", f"video/x-raw,width={config.resolution.split('x')[0]},height={config.resolution.split('x')[1]},framerate={config.framerate}/1",
            "!", "x264enc", "tune=zerolatency", f"bitrate={config.bitrate}",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location=rtsp://video-processor:8556/annotated_{stream_name}"
        ]
        subprocess.Popen(command)

    streams[config.type][stream_name] = {
        "source": config.source,
        "resolution": config.resolution,
        "framerate": config.framerate,
        "bitrate": config.bitrate,
        "status": "active"
    }
    return {"message": f"Started {config.type} stream at rtsp://video-processor:8556/{stream_name}", "stream_name": stream_name}

@app.post("/streams/stop")
def stop_stream(stream_name: str, stream_type: str):
    if stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")
    if stream_name not in streams[stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")
    streams[stream_type][stream_name]["status"] = "inactive"
    return {"message": f"Stopped {stream_type} stream {stream_name}"}

@app.post("/streams/update")
def update_stream(params: StreamUpdate):
    if params.stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")
    if params.stream_name not in streams[params.stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")
    stream = streams[params.stream_type][params.stream_name]
    if params.resolution:
        stream["resolution"] = params.resolution
    if params.framerate:
        stream["framerate"] = params.framerate
    if params.bitrate:
        stream["bitrate"] = params.bitrate
    return {"message": f"Updated {params.stream_type} stream {params.stream_name}", "stream": stream}

@app.get("/streams/status")
def stream_status():
    return streams

@app.get("/analytics/metrics")
def get_analytics_metrics():
    return JSONResponse(content=analytics.get_metrics())