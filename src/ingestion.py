import subprocess

# Base RTSP URL
rtsp_base_url = "rtsp://0.0.0.0:8554/"

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name, is_local=True):
    full_url = f"{rtsp_base_url}{stream_name}"
    if is_local:
        command = [
            "gst-launch-1.0",
            "v4l2src", f"device={source}",
            "!", "videoconvert",
            "!", "x264enc", "tune=zerolatency",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location={full_url}"
        ]
    else:
        command = [
            "gst-launch-1.0",
            "httpsrc", f"location={source}",
            "!", "rtph264depay",
            "!", "avdec_h264",
            "!", "videoconvert",
            "!", "x264enc", "tune=zerolatency",
            "!", "rtph264pay", "pt=96",
            "!", f"rtspclientsink location={full_url}"
        ]
    print(f"Starting RTSP stream: {full_url}")
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return full_url