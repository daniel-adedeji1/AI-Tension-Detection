import zmq
import json
import uuid
import time

context = zmq.Context()
socket = context.socket(zmq.PUSH)

socket.connect("tcp://localhost:5556")

while True:

    event_id = str(uuid.uuid4())

    metadata = {
        "packet_type": "incident_start",
        "event_id": event_id,
        "camera_id": "1",
        "trigger_reason": "SHOUTING DETECTED (confidence=0.82)",
        "employee_name": "John Doe",
        "trigger_ts": time.time(),
    }

    kind = "event"
    payload = b""  # your Django doesn't use it for incident_start

    socket.send_multipart([
        kind.encode("utf-8"),
        json.dumps(metadata).encode("utf-8"),
        payload
    ])

    print("Sent incident_start:", event_id)

    time.sleep(3)