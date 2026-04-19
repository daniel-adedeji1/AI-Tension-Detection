import json
from unittest import mock

from asgiref.sync import async_to_sync, sync_to_async
from asgiref.testing import ApplicationCommunicator as BaseApplicationCommunicator
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from .consumers import AlertConsumer
from .models import Alert


TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


def no_op():
    pass


class ApplicationCommunicator(BaseApplicationCommunicator):
    async def send_input(self, message):
        with mock.patch("channels.db.close_old_connections", no_op):
            return await super().send_input(message)

    async def receive_output(self, timeout=1):
        with mock.patch("channels.db.close_old_connections", no_op):
            return await super().receive_output(timeout)


@override_settings(
    CHANNEL_LAYERS=TEST_CHANNEL_LAYERS,
    ENABLE_ALERT_TEST_ENDPOINT=True,
    AUTO_START_ZMQ_LISTENER=False,
    ALERT_TEST_TRANSPORT="direct",
)
class TestAlertFlow(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_test_endpoint_creates_alert_record(self):
        response = self.client.post(
            "/api/users/alerts/test/",
            {
                "camera_id": "camera-7",
                "employee_name": "Smoke Test User",
                "trigger_reason": "Manual verification run",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Alert.objects.count(), 1)

        alert = Alert.objects.get()
        self.assertEqual(alert.camera_id, "camera-7")
        self.assertEqual(alert.employee_name, "Smoke Test User")
        self.assertEqual(alert.trigger_reason, "Manual verification run")

    def test_test_endpoint_broadcasts_alert_over_websocket(self):
        response_status, payload = async_to_sync(self._broadcast_and_receive_alert)()
        self.assertEqual(response_status, 201)
        self.assertEqual(payload["packet_type"], "incident_start")
        self.assertEqual(payload["camera_id"], "camera-3")
        self.assertEqual(payload["employee_name"], "Alert Tester")
        self.assertEqual(payload["trigger_reason"], "Websocket smoke test")

    def test_stop_recording_resolves_existing_alert(self):
        create_response = self.client.post(
            "/api/users/alerts/test/",
            {
                "camera_id": "camera-2",
                "employee_name": "Resolve Tester",
                "trigger_reason": "Resolve endpoint test",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        event_id = create_response.json()["event_id"]

        resolve_response = self.client.post(
            "/api/recordings/stop/",
            {
                "event_id": event_id,
                "camera_id": "camera-2",
                "reason": "manager_clear",
            },
            format="json",
        )

        self.assertEqual(resolve_response.status_code, 200)
        self.assertEqual(resolve_response.json()["packet_type"], "incident_resolved")
        self.assertFalse(Alert.objects.filter(event_id=event_id).exists())

    def test_alert_list_returns_created_alerts(self):
        create_response = self.client.post(
            "/api/users/alerts/test/",
            {
                "camera_id": "camera-9",
                "employee_name": "List Tester",
                "trigger_reason": "List endpoint test",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)

        list_response = self.client.get("/api/users/alerts/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(list_response.json()[0]["employee_name"], "List Tester")

    async def _broadcast_and_receive_alert(self):
        communicator = ApplicationCommunicator(
            AlertConsumer.as_asgi(),
            {
                "type": "websocket",
                "path": "/ws/alerts/",
                "headers": [],
                "query_string": b"",
            },
        )
        await communicator.send_input({"type": "websocket.connect"})
        connect_response = await communicator.receive_output(timeout=1)
        self.assertEqual(connect_response["type"], "websocket.accept")

        response = await sync_to_async(self.client.post, thread_sensitive=True)(
            "/api/users/alerts/test/",
            {
                "camera_id": "camera-3",
                "employee_name": "Alert Tester",
                "trigger_reason": "Websocket smoke test",
            },
            format="json",
        )
        message = await communicator.receive_output(timeout=1)
        payload = json.loads(message["text"])
        await communicator.send_input({"type": "websocket.disconnect", "code": 1000})
        return response.status_code, payload
