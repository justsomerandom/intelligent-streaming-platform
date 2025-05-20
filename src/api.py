from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import analytics
import ingestion
import streaming
from typing import Optional

app = FastAPI()

# In-memory store for active streams and analytics
streams = {
    "raw": {},
    "annotated": {}
}
analytics_metrics = {}

class StreamConfig(BaseModel):
    stream_name: str
    source: str | int
    type: str  # "raw" or "annotated"
    resolution: str = "640x480"
    framerate: int = 30
    bitrate: str = "1M"
    is_local: bool = False

class StreamUpdate(BaseModel):
    stream_name: str
    stream_type: str  # "raw" or "annotated"
    resolution: Optional[str] = None
    framerate: Optional[int] = None
    bitrate: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Intelligent Multi-Source Video Platform API"}

@app.get("/api/streams")
def list_streams():
    return streams

@app.post("/api/streams/start")
def start_stream(config: StreamConfig):
    if config.type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")

    if config.type == "raw":
        ingestion.start_rtsp_stream(config.source, config.stream_name, config.resolution, config.is_local)
    else:
        res = config.resolution.split("x")
        streaming.start_annotated_stream(config.stream_name, int(res[0]), int(res[1]), config.framerate)

    streams[config.type][config.stream_name] = {
        "source": config.source,
        "resolution": config.resolution,
        "framerate": config.framerate,
        "bitrate": config.bitrate,
        "status": "active"
    }
    return {"message": f"Started {config.type} stream at rtsp://localhost:8554/{config.stream_name}", "stream_name": config.stream_name}

@app.post("/api/streams/stop")
def stop_stream(stream_name: str, stream_type: str):
    if stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")
    if stream_name not in streams[stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")
    streams[stream_type][stream_name]["status"] = "inactive"
    return {"message": f"Stopped {stream_type} stream {stream_name}"}

@app.post("/api/streams/update")
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

@app.get("/api/streams/status")
def stream_status():
    return streams

@app.get("/api/streams/active")
def list_all_active_streams():
    all_active = []
    for stream_type in ["raw", "annotated"]:
        for name, s in streams.get(stream_type, {}).items():
            if s.get("status") == "active":
                all_active.append({
                    "name": name,
                    "type": stream_type,
                    "url": f"rtsp://localhost:8554/{name}"
                })
    return {"streams": all_active}


@app.get("/api/analytics/metrics")
def get_analytics_metrics():
    return JSONResponse(content=analytics.get_metrics())
