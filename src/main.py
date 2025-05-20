import asyncio
import uvicorn
import analytics
import ingestion
import api
import streaming
import requests
import cv2
import platform
import os
import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

# List of video sources (can be /dev/video*, IP cameras, or MJPEG/RTSP)
video_sources = []
ip_host = os.getenv("IP_HOST", "localhost")
is_local = os.getenv("IS_LOCAL", "true").lower() == "true"

def start_api():
    config = uvicorn.Config("api:app", host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    return server.serve()

def get_video_sources():
    global video_sources
    if os.path.exists("/dev"):
        video_devices = [os.path.join("/dev", d) for d in os.listdir("/dev") if d.startswith("video")]
        video_sources.extend(video_devices)
    if is_local and platform.system() == "Windows":
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                cap.release()
                break
            video_sources.append(str(index))
            cap.release()
            index += 1
    else:
        try:
            served_sources = requests.get(f"http://{ip_host}:8081/cams")
            if served_sources.status_code == 200:
                served_sources = served_sources.json().get("cameras", [])
                for source in served_sources:
                    if source not in video_sources:
                        video_sources.append(source)
        except requests.RequestException as e:
            print(f"Error fetching camera sources: {e}")

async def process_camera_streams():
    urls = []

    annotated_fps = 25
    for i, source in enumerate(video_sources):
        stream_name = f"camera{i}"

        is_local = source.startswith("/dev/video") or source.isdigit()
        url = f"rtsp://localhost:8554/{stream_name}"
        urls.append(url)
        raw_config = api.StreamConfig(
            source=source,
            type="raw",
            stream_name=stream_name,
            is_local=is_local,
            resolution="1280x720",
        )
        api.start_stream(raw_config)

        annotated_stream_name = f"annotated_camera{i}"
        annotated_config = api.StreamConfig(
            source=source,
            type="annotated",
            stream_name=annotated_stream_name,
            is_local=is_local,
            resolution="1280x720",
            framerate=annotated_fps,
        )
        api.start_stream(annotated_config)

    await asyncio.sleep(5)

    for url in urls:
        executor.submit(analytics.process_stream, url)
    


async def main():
    get_video_sources()

    # Start the API server (runs forever)
    api_task = asyncio.create_task(start_api())

    # Start stream processing
    analytics_task = asyncio.create_task(process_camera_streams())

    await asyncio.gather(api_task, analytics_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
