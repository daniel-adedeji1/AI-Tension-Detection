from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import zmq

from .models import Alert


def broadcast_alert(payload):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        raise RuntimeError("No channel layer is configured for alert broadcasts.")

    async_to_sync(channel_layer.group_send)(
        "alerts",
        {
            "type": "alert_message",
            "data": payload,
        },
    )


def process_alert_packet(data):
    packet_type = data.get("packet_type")

    if packet_type == "incident_start":
        alert = Alert.objects.create(
            event_id=data["event_id"],
            camera_id=data["camera_id"],
            trigger_reason=data["trigger_reason"],
            employee_name=data.get("employee_name", ""),
        )

        payload = {
            "packet_type": "incident_start",
            "event_id": str(alert.event_id),
            "camera_id": alert.camera_id,
            "trigger_reason": alert.trigger_reason,
            "employee_name": alert.employee_name,
            "timestamp": alert.timestamp.isoformat(),
        }
        broadcast_alert(payload)
        return payload

    if packet_type == "frame":
        payload = {
            "packet_type": "frame",
            "event_id": data["event_id"],
            "frame": data["jpeg_base64"],
            "timestamp": data["frame_ts"],
        }
        broadcast_alert(payload)
        return payload

    if packet_type == "audio":
        broadcast_alert(data)
        return data

    raise ValueError(f"Unsupported packet_type: {packet_type!r}")


def resolve_alert(alert, reason="manager_clear"):
    payload = {
        "packet_type": "incident_resolved",
        "event_id": str(alert.event_id),
        "camera_id": alert.camera_id,
        "employee_name": alert.employee_name,
        "reason": reason,
    }
    alert.delete()
    broadcast_alert(payload)
    return payload


def send_packet_over_zmq(data, address):
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)

    try:
        socket.connect(address)
        socket.send_json(data)
    finally:
        socket.close()
