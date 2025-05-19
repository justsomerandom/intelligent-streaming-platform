import subprocess
import re
import time
import os
from dotenv import load_dotenv

load_dotenv()
start_port = int(os.getenv("MIN_PORT", 8081))
final_port = int(os.getenv("MAX_PORT", 8090))

# Step 1: Get list of video devices via ffmpeg
def get_video_devices():
    result = subprocess.run(
        ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True,
        text=True
    )
    matches = re.findall(r'\[dshow @ .*?\] *"([^"]+)"\s*\(.*video.*\)', result.stderr, re.IGNORECASE)
    return matches

# Step 2: Start an ffmpeg stream for each device
def stream_devices(devices, starting_port=start_port):
    for i, device in enumerate(devices):
        port = starting_port + i
        print(f"Streaming '{device}' on port {port}")
        command = [
            "ffmpeg",
            "-f", "dshow",
            "-i", f"video={device}",
            "-vf", "scale=640:480",
            "-f", "mjpeg",
            f"http://localhost:{port}/webcam.mjpg"
        ]
        subprocess.Popen(command)  # No wait, stream in background

if __name__ == "__main__":
    devices = get_video_devices()
    if not devices:
        print("No video devices found.")
    else:
        print("Detected devices:", devices)
        stream_devices(devices)
        print("Streaming. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Exiting.")
