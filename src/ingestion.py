import subprocess
import cv2
import threading
from stream_settings import bitrate_to_kbps

# Base RTSP URL
rtsp_base_url = "rtsp://localhost:8554/"
stream_processes = {}


def _stop_process(proc):
    if proc.stdin is not None:
        try:
            proc.stdin.close()
        except OSError:
            pass

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def stop_rtsp_stream(stream_name):
    """Stop and forget the GStreamer process associated with ``stream_name``."""
    proc = stream_processes.pop(stream_name, None)
    if proc is None:
        return False
    _stop_process(proc)
    return True

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name, resolution, is_local=True, framerate=30, bitrate="1M"):
    """Launch a raw stream using the requested frame rate and encoder bitrate."""
    stop_rtsp_stream(stream_name)
    source = str(source)
    width, height = resolution.split("x")
    bitrate_kbps = bitrate_to_kbps(bitrate)
    full_url = f"{rtsp_base_url}{stream_name}"
    if is_local:
        if source.startswith("/dev/video"):
            print(f"Starting RTSP stream for local device: {source}")
            command = [
                "gst-launch-1.0", "v4l2src", f"device={source}", "!",
                f"video/x-raw,width={width},height={height},framerate={framerate}/1",
                "!", "videoconvert", "!", "x264enc", "tune=zerolatency", f"bitrate={bitrate_kbps}", "!",
                "h264parse", "!", "rtspclientsink", f"location={full_url}",
            ]
        else:
            print(f"Starting RTSP stream for local Windows video source: {source}")
            command = [
                "gst-launch-1.0", "mfvideosrc", f"device-index={source}", "!",
                f"video/x-raw,width={width},height={height},framerate={framerate}/1",
                "!", "videoconvert", "!", "x264enc", "tune=zerolatency", f"bitrate={bitrate_kbps}", "!",
                "h264parse", "!", "rtspclientsink", f"location={full_url}",
            ]
    else:
        print(f"Starting RTSP stream for IP source: {source}")
        command = [
            "gst-launch-1.0", "souphttpsrc", f"location={source}", "!",
                f"video/x-raw,width={width},height={height},framerate={framerate}/1",
                "!", "jpegdec", "!", "videoconvert", "!", "x264enc", "tune=zerolatency", f"bitrate={bitrate_kbps}",
            "!", "h264parse", "!", "rtspclientsink", f"location={full_url}",
        ]
    print(f"Starting RTSP stream: {full_url}")
    stream_processes[stream_name] = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return full_url
