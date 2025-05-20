import subprocess
import cv2
import threading

# Base RTSP URL
rtsp_base_url = "rtsp://localhost:8554/"

# Function to start an RTSP stream for each source
def start_rtsp_stream(source, stream_name, is_local=True):
    full_url = f"{rtsp_base_url}{stream_name}"
    if is_local:
        if source.startswith("/dev/video"):
            print(f"Starting RTSP stream for local device: {source}")
            command = (
                f'gst-launch-1.0 '
                f'v4l2src device={source} '
                f'! videoconvert '
                f'! x264enc tune=zerolatency '
                f'! h264parse '
                f'! rtspclientsink location={full_url}'
            )
        else:
            print(f"Starting RTSP stream for local Windows video source: {source}")
            command = (
                f'gst-launch-1.0 '
                f'mfvideosrc device-index={source} '
                f'! videoconvert '
                f'! x264enc tune=zerolatency '
                f'! h264parse '
                f'! rtspclientsink location={full_url}'
            )
    else:
        print(f"Starting RTSP stream for IP source: {source}")
        command = (
            f'gst-launch-1.0 '
            f'souphttpsrc location={source} '
            f'! jpegdec '
            f'! videoconvert '
            f'! x264enc tune=zerolatency '
            f'! h264parse '
            f'! rtspclientsink location={full_url}'
        )
    print(f"Starting RTSP stream: {full_url}")
    subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return full_url