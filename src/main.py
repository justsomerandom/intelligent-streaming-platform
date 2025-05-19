import asyncio
import uvicorn
import analytics
import ingestion
import streaming
import requests
import os

# List of video sources (can be /dev/video*, IP cameras, or MJPEG/RTSP)
video_sources = []

def start_api():
    config = uvicorn.Config("api:app", host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    return server.serve()

def get_video_sources():
    global video_sources
    if os.path.exists("/dev"):
        video_devices = [os.path.join("/dev", d) for d in os.listdir("/dev") if d.startswith("video")]
        video_sources.extend(video_devices)
    served_sources = requests.get("http://docker.internal.host:8081/cams")
    if served_sources.status_code == 200:
        served_sources = served_sources.json().get("cameras", [])
        for source in served_sources:
            if source not in video_sources:
                video_sources.append(source)

async def process_camera_streams():
    for i, source in enumerate(video_sources):
        stream_name = f"camera{i}"

        # Start ingesting from source and get internal RTSP URL
        if source.startswith("/dev/"):
            url = ingestion.start_rtsp_stream(source, stream_name, is_local=True)
        else:
            url = ingestion.start_rtsp_stream(source, stream_name, is_local=False)

        # Start raw streaming (e.g., to GStreamer pipeline or WebRTC)
        streaming.start_stream(stream_name, url)

        # Start annotated stream (optional: delay or signal after analysis starts)
        annotated_stream_name = f"annotated_camera{i}"
        streaming.start_annotated_stream(annotated_stream_name, 640, 480, fps=25)

        # Start analytics processing on this stream
        asyncio.create_task(analytics.process_stream(url))

async def main():
    get_video_sources()
    await asyncio.gather(
        start_api(),
        process_camera_streams()
    )

if __name__ == "__main__":
    asyncio.run(main())
