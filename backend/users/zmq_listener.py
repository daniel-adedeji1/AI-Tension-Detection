import zmq
from django.conf import settings
from .alert_service import process_alert_packet

def run_listener():
    print("ZMQ Listener started...")
    context = zmq.Context.instance()
    socket = context.socket(zmq.PULL)
    socket.bind(settings.ZMQ_INGEST_BIND_ADDRESS)

    try:
        while True:
            process_alert_packet(socket.recv_json())
    finally:
        socket.close()
