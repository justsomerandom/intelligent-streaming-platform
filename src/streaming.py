import subprocess
import cv2
import numpy as np
from stream_settings import bitrate_to_kbps
from stream_process import process_health, stop_process

stream_processes = {}


def stop_annotated_stream(name):
    """Stop and forget the GStreamer process associated with ``name``."""
    proc = stream_processes.pop(name, None)
    if proc is None:
        return False
    stop_process(proc)
    return True


def get_annotated_stream_health(name):
    """Return whether the named annotated-stream pipeline is still alive."""
    return process_health(stream_processes.get(name))


def start_annotated_stream(name, width, height, fps=25, bitrate="1M"):
    """Launch an annotated stream using the requested frame rate and bitrate."""
    stop_annotated_stream(name)
    bitrate_kbps = bitrate_to_kbps(bitrate)

    command = [
        "gst-launch-1.0", "-v", "fdsrc", "fd=0", f"blocksize={width * height * 3}", "!",
        "rawvideoparse", f"width={width}", f"height={height}", "format=rgb", f"framerate={fps}/1",
        "!", "videoconvert", "!", "x264enc", "speed-preset=ultrafast", "tune=zerolatency", f"bitrate={bitrate_kbps}",
        "!", "h264parse", "!", "rtspclientsink", f"location=rtsp://localhost:8554/{name}",
    ]

    print(f"Starting annotated stream for {name} at rtsp://localhost:8554/{name}")
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    stream_processes[name] = proc
    dummy = np.zeros((height, width, 3), dtype=np.uint8)
    rgb_dummy = cv2.cvtColor(dummy, cv2.COLOR_BGR2RGB)
    proc.stdin.write(rgb_dummy.tobytes())

def stream_annotated_frame(frame, name):
    global stream_processes
    proc = stream_processes.get(name)
    if proc is None or proc.stdin is None:
        print(f"No stream process found for {name}. Did you call start_annotated_stream?")
        return
    # Ensure frame is in RGB and contiguous
    if frame.shape[2] == 3:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        rgb_frame = frame
    proc.stdin.write(rgb_frame.tobytes())
