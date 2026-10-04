import subprocess
import cv2
import threading

# Base RTSP URL
rtsp_base_url = "rtsp://localhost:8554/"

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name, resolution, is_local=True):
    full_url = f"{rtsp_base_url}{stream_name}"
    if is_local:
        if source.startswith("/dev/video"):
            print(f"Starting RTSP stream for local device: {source}")
            command = [
                "gst-launch-1.0", "v4l2src", f"device={source}", "!",
                f"video/x-raw,width={resolution.split('x')[0]},height={resolution.split('x')[1]}",
                "!", "videoconvert", "!", "x264enc", "tune=zerolatency", "!",
                "h264parse", "!", "rtspclientsink", f"location={full_url}",
            ]
        else:
            print(f"Starting RTSP stream for local Windows video source: {source}")
            command = [
                "gst-launch-1.0", "mfvideosrc", f"device-index={source}", "!",
                f"video/x-raw,width={resolution.split('x')[0]},height={resolution.split('x')[1]}",
                "!", "videoconvert", "!", "x264enc", "tune=zerolatency", "!",
                "h264parse", "!", "rtspclientsink", f"location={full_url}",
            ]
    else:
        print(f"Starting RTSP stream for IP source: {source}")
        command = [
            "gst-launch-1.0", "souphttpsrc", f"location={source}", "!",
            f"video/x-raw,width={resolution.split('x')[0]},height={resolution.split('x')[1]}",
            "!", "jpegdec", "!", "videoconvert", "!", "x264enc", "tune=zerolatency",
            "!", "h264parse", "!", "rtspclientsink", f"location={full_url}",
        ]
    print(f"Starting RTSP stream: {full_url}")
    subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return full_url
