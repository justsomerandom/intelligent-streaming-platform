from core import analytics
from core import ingestion
from core import streaming

# Defining the list of video sources (webcams, IP cameras)
video_sources = [
    "/dev/video0",  # Local webcam (Linux)
    "/dev/video1",  # Second webcam (Linux)
    "rtsp://your_ip_camera_url"  # IP Camera
]

async def stream_on_unlock(stream_name):
    analytics.url_unlock.wait()
    streaming.start_stream(f"{stream_name}-annotated", analytics.url_lock)
    analytics.lock()

for i, source in enumerate(video_sources):
    stream_name = f"camera{i}"
    url = ingestion.start_rtsp_stream(source, stream_name)
    streaming.start_stream(stream_name, url)

    analytics.process_stream(url)
    stream_on_unlock(stream_name)