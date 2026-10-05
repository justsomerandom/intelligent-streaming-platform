from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import analytics
import ingestion
import streaming
from stream_settings import bitrate_to_kbps
from typing import Optional
import re

app = FastAPI()

# In-memory store for active streams and analytics
streams = {
    "raw": {},
    "annotated": {}
}
analytics_metrics = {}

RESOLUTION_PATTERN = re.compile(r"^[1-9]\d{0,4}x[1-9]\d{0,4}$")
STREAM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

class StreamConfig(BaseModel):
    stream_name: str
    source: str | int
    type: str  # "raw" or "annotated"
    resolution: str = "640x480"
    framerate: int = Field(default=30, ge=1)
    bitrate: str = "1M"
    is_local: bool = False

    @validator("resolution")
    def validate_resolution(cls, value):
        if not RESOLUTION_PATTERN.fullmatch(value):
            raise ValueError("resolution must be WIDTHxHEIGHT with positive integer dimensions")
        return value

    @validator("stream_name")
    def validate_stream_name(cls, value):
        if not STREAM_NAME_PATTERN.fullmatch(value):
            raise ValueError("stream_name must contain only letters, numbers, underscores, or hyphens")
        return value

    @validator("bitrate")
    def validate_bitrate(cls, value):
        bitrate_to_kbps(value)
        return value

class StreamUpdate(BaseModel):
    stream_name: str
    stream_type: str  # "raw" or "annotated"
    resolution: Optional[str] = None
    framerate: Optional[int] = Field(default=None, ge=1)
    bitrate: Optional[str] = None

    @validator("resolution")
    def validate_resolution(cls, value):
        if value is not None and not RESOLUTION_PATTERN.fullmatch(value):
            raise ValueError("resolution must be WIDTHxHEIGHT with positive integer dimensions")
        return value

    @validator("stream_name")
    def validate_stream_name(cls, value):
        if not STREAM_NAME_PATTERN.fullmatch(value):
            raise ValueError("stream_name must contain only letters, numbers, underscores, or hyphens")
        return value

    @validator("bitrate")
    def validate_bitrate(cls, value):
        if value is not None:
            bitrate_to_kbps(value)
        return value


def _launch_stream(stream_type, stream):
    """Start a pipeline from its persisted API configuration."""
    if stream_type == "raw":
        return ingestion.start_rtsp_stream(
            stream["source"],
            stream["stream_name"],
            stream["resolution"],
            stream["is_local"],
            stream["framerate"],
            stream["bitrate"],
        )

    width, height = map(int, stream["resolution"].split("x"))
    return streaming.start_annotated_stream(
        stream["stream_name"], width, height, stream["framerate"], stream["bitrate"]
    )


def _stop_stream_pipeline(stream_type, stream_name):
    if stream_type == "raw":
        return ingestion.stop_rtsp_stream(stream_name)
    return streaming.stop_annotated_stream(stream_name)

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

    stream = {
        "stream_name": config.stream_name,
        "source": config.source,
        "is_local": config.is_local,
        "resolution": config.resolution,
        "framerate": config.framerate,
        "bitrate": config.bitrate,
        "status": "active"
    }
    try:
        _launch_stream(config.type, stream)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"Unable to start stream: {error}") from error

    streams[config.type][config.stream_name] = stream
    return {"message": f"Started {config.type} stream at rtsp://localhost:8554/{config.stream_name}", "stream_name": config.stream_name}

@app.post("/api/streams/stop")
def stop_stream(stream_name: str, stream_type: str):
    if stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")
    if stream_name not in streams[stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")
    _stop_stream_pipeline(stream_type, stream_name)
    streams[stream_type][stream_name]["status"] = "inactive"
    return {"message": f"Stopped {stream_type} stream {stream_name}"}

@app.post("/api/streams/update")
def update_stream(params: StreamUpdate):
    if params.stream_type not in ["raw", "annotated"]:
        raise HTTPException(status_code=400, detail="Invalid stream type")
    if params.stream_name not in streams[params.stream_type]:
        raise HTTPException(status_code=404, detail="Stream not found")
    stream = streams[params.stream_type][params.stream_name]
    updated_stream = stream.copy()
    if params.resolution is not None:
        updated_stream["resolution"] = params.resolution
    if params.framerate is not None:
        updated_stream["framerate"] = params.framerate
    if params.bitrate is not None:
        updated_stream["bitrate"] = params.bitrate

    try:
        _launch_stream(params.stream_type, updated_stream)
    except (OSError, ValueError) as error:
        stream["status"] = "error"
        stream["last_error"] = str(error)
        raise HTTPException(status_code=502, detail=f"Unable to apply stream settings: {error}") from error

    streams[params.stream_type][params.stream_name] = updated_stream
    return {"message": f"Updated {params.stream_type} stream {params.stream_name}", "stream": updated_stream}

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
