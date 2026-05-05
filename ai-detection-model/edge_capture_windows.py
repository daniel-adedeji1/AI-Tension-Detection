import cv2
import sounddevice as sd
import numpy as np
import zmq
import time
import json

context = zmq.Context()
socket = context.socket(zmq.PUSH)

# Connect to WSL
socket.connect("tcp://172.28.227.153:5557")

# ---------------- VIDEO ----------------
cap = cv2.VideoCapture(0)

# ---------------- AUDIO ----------------
sample_rate = 16000
chunk_size = int(sample_rate * 1.0)

def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)

    audio = indata.flatten().astype(np.float32)

    metadata = {"ts": time.time()}

    socket.send_multipart([
        b"audio",
        json.dumps(metadata).encode(),
        audio.tobytes()
    ])

stream = sd.InputStream(
    samplerate=sample_rate,
    channels=1,
    callback=audio_callback
)

stream.start()

print("🚀 Sensor producer running...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    _, jpg = cv2.imencode(".jpg", frame)

    metadata = {"ts": time.time()}

    socket.send_multipart([
        b"video",
        json.dumps(metadata).encode(),
        jpg.tobytes()
    ])

    time.sleep(1/30)