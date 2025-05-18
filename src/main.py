import asyncio
import uvicorn
import analytics
import ingestion
import streaming

# List of video sources (can be /dev/video*, IP cameras, or MJPEG/RTSP)
video_sources = [
    "/dev/video0",
    "/dev/video1",
    "rtsp://your_ip_camera_url"
]

def start_metrics_api():
    config = uvicorn.Config("api:app", host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    return server.serve()

async def process_camera_streams():
    for i, source in enumerate(video_sources):
        stream_name = f"camera{i}"

        # Start ingesting from source and get internal RTSP URL
        url = ingestion.start_rtsp_stream(source, stream_name)

        # Start raw streaming (e.g., to GStreamer pipeline or WebRTC)
        streaming.start_stream(stream_name, url)

        # Start annotated stream (optional: delay or signal after analysis starts)
        annotated_stream_name = f"annotated_camera{i}"
        streaming.start_annotated_stream(annotated_stream_name, 640, 480, fps=25)

        # Start analytics processing on this stream
        asyncio.create_task(analytics.process_stream(url))

async def main():
    await asyncio.gather(
        start_metrics_api(),
        process_camera_streams()
    )

if __name__ == "__main__":
    asyncio.run(main())
