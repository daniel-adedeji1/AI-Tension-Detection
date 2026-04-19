import zmq
import json
import uuid
import time

context = zmq.Context()
socket = context.socket(zmq.PUSH)

socket.connect("tcp://localhost:5555")

while True:
    mock_data = {
        "packet_type": "incident_start",
        "event_id": str(uuid.uuid4()),
        "camera_id": 1,
        "employee_name": "John Doe (Simulated)",
        "trigger_reason": "Shout tony detected hello (confidence=0.89)"
    }

    print("Sending:", mock_data["event_id"])
    socket.send_json(mock_data)

    time.sleep(3)