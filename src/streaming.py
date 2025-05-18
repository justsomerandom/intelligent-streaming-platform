import subprocess
import cv2

stream_processes = {}

def start_stream(name, src_url):
    command = [
        "gst-launch-1.0",
        "rtspsrc", f"location={src_url}",
        "!", "rtph264depay", 
        "!", "h264parse",
        "!", "rtph264pay", "pt=96",
        "!", f"rtspclientsink location=rtsp://0.0.0.0:8556/{name}"
    ]
    print(f"Starting Streaming for {name} at rtsp://0.0.0.0:8556/{name}")
    subprocess.Popen(command)

def start_annotated_stream(name, width, height, fps=25):
    global stream_processes
    command = [
        "gst-launch-1.0",
        "fdsrc", "!",
        f"rawvideoparse width={width} height={height} format=rgb",
        "!", "videoconvert",
        "!", "x264enc speed-preset=ultrafast tune=zerolatency",
        "!", "rtph264pay", "pt=96",
        "!", f"rtspclientsink location=rtsp://0.0.0.0:8556/{name}"
    ]
    print(f"Starting annotated stream for {name} at rtsp://0.0.0.0:8556/{name}")
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    stream_processes[name] = proc

async def stream_annotated_frame(frame, name):
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