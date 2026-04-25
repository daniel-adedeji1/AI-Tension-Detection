import zmq
import json
from django.conf import settings
from .alert_service import process_alert_packet

def run_listener():
    print("ZMQ Listener started...")
    context = zmq.Context.instance()
    socket = context.socket(zmq.PULL)
    socket.bind(settings.ZMQ_INGEST_BIND_ADDRESS)

    try:
        while True:
            # Receive multipart message from edge pipeline
            kind, metadata_bytes, payload = socket.recv_multipart()

            metadata = json.loads(metadata_bytes.decode("utf-8"))

            packet = {
                "packet_type": metadata.get("packet_type"),  # you may need to fix this upstream too
                **metadata,
                "kind": kind.decode("utf-8"),
                "payload": payload,
            }

            process_alert_packet(packet)

    finally:
        socket.close()