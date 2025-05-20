import tkinter as tk
from tkinter import ttk
import cv2
import threading
import requests

# Global state
current_stream_thread = None
stop_stream_flag = False
current_stream_url = None

def fetch_streams():
    try:
        res = requests.get("http://localhost:8080/api/streams/active")
        return [s['url'] for s in res.json().get('streams', [])]
    except Exception as e:
        print("Failed to fetch streams:", e)
        return []

def start_stream(rtsp_url):
    global stop_stream_flag, current_stream_url

    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print(f"Cannot open stream: {rtsp_url}")
        return

    print(f"Streaming from: {rtsp_url}")
    while cap.isOpened() and not stop_stream_flag:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended or lost.")
            break
        cv2.imshow("RTSP Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Stream closed: {rtsp_url}")

def on_select(event):
    global current_stream_thread, stop_stream_flag, current_stream_url

    selected_url = stream_var.get()
    if selected_url == current_stream_url:
        print("Same stream selected. Ignoring.")
        return

    # Signal existing stream to stop
    stop_stream_flag = True
    if current_stream_thread and current_stream_thread.is_alive():
        current_stream_thread.join()

    # Reset and start new stream
    stop_stream_flag = False
    current_stream_url = selected_url
    current_stream_thread = threading.Thread(target=start_stream, args=(selected_url,), daemon=True)
    current_stream_thread.start()

def on_close():
    global stop_stream_flag
    stop_stream_flag = True
    if current_stream_thread and current_stream_thread.is_alive():
        current_stream_thread.join()
    root.destroy()

# UI Setup
root = tk.Tk()
root.title("Camera Stream Viewer")

tk.Label(root, text="Select RTSP Stream:").pack(pady=10)

stream_var = tk.StringVar()
streams = fetch_streams()
dropdown = ttk.Combobox(root, textvariable=stream_var, values=streams, width=50)
dropdown.bind("<<ComboboxSelected>>", on_select)
dropdown.pack()

tk.Button(root, text="Refresh", command=lambda: dropdown.config(values=fetch_streams())).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
