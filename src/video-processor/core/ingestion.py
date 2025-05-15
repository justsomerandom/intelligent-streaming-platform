import subprocess

# Base RTSP URL
rtsp_base_url = "rtsp://0.0.0.0:8554/"

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name):
    full_url = f"{rtsp_base_url}{stream_name}"
    command = [
        "gst-launch-1.0",
        "v4l2src", f"device={source}",
        "!", "videoconvert",
        "!", "x264enc", "tune=zerolatency",
        "!", "rtph264pay", "pt=96",
        "!", f"rtspclientsink location={full_url}"
    ]
    print(f"Starting RTSP stream: {full_url}")
    subprocess.Popen(command)
    return full_url