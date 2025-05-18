import asyncio
import uvicorn
from core import analytics
from core import ingestion
from core import streaming

# Defining the list of video sources (webcams, IP cameras)
video_sources = [
    "/dev/video0",  # Local webcam (Linux)
    "/dev/video1",  # Second webcam (Linux)
    "rtsp://your_ip_camera_url"  # IP Camera
]

async def main():
    asyncio.create_task(uvicorn.run("core.analytics:app", host="0.0.0.0", port=8001))
    for i, source in enumerate(video_sources):
        stream_name = f"camera{i}"
        url = ingestion.start_rtsp_stream(source, stream_name)
        streaming.start_stream(stream_name, url)

        stream_name = f"annotated_camera{i}"
        streaming.start_annotated_stream(stream_name, 640, 480, fps=25)
        asyncio.create_task(analytics.process_stream(url))

if __name__ == "__main__":
    asyncio.run(main())