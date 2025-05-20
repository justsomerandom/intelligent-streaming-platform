import subprocess
import cv2

stream_processes = {}

def start_annotated_stream(name, width, height, fps=25):
    global stream_processes
    command = (
        f'gst-launch-1.0 '
        f'fdsrc '
        f'! rawvideoparse width={width} height={height} format=rgb '
        f'! videoconvert '
        f'! x264enc speed-preset=ultrafast tune=zerolatency '
        f'! h264parse '
        f'! rtspclientsink location=rtsp://localhost:8554/{name}'
    )
    print(f"Starting annotated stream for {name} at rtsp://localhost:8554/{name}")
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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