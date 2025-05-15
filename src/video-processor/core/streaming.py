import subprocess

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
