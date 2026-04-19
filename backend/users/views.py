from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import User, Alert #, Video
from rest_framework import generics, status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .serializers import AlertSerializer, UserSerializer, UserCreateSerializer #, VideoSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.authentication import BaseAuthentication # type: ignore
from rest_framework.exceptions import AuthenticationFailed # type: ignore
from .authentication import CustomSessionAuthentication
from django.http import StreamingHttpResponse
from rest_framework.exceptions import PermissionDenied, ValidationError # type: ignore
import uuid
import psycopg2
from .alert_service import process_alert_packet, resolve_alert, send_packet_over_zmq

# Create your views here.
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [IsAuthenticated]


class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.order_by("-timestamp")
    serializer_class = AlertSerializer
    permission_classes = [AllowAny]

"""   
class VideoListAPIView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset
"""
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        password = request.data.get('e_password')

        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)

        if not check_password(password, user.e_password_hash):
            return Response({'error': 'Invalid credentials'}, status=401)

        request.session.flush()
        request.session['employee_id'] = str(user.employee_id)
        request.session['is_authenticated'] = True

        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        request.session.flush()
        return Response({"message": "Logged out"}, status=200)


class TestAlertView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.ENABLE_ALERT_TEST_ENDPOINT:
            raise PermissionDenied("Alert testing is disabled.")

        packet_type = request.data.get("packet_type", "incident_start")
        if packet_type != "incident_start":
            raise ValidationError({"packet_type": "Only incident_start is supported by the test endpoint."})

        payload = {
            "packet_type": "incident_start",
            "event_id": request.data.get("event_id") or str(uuid.uuid4()),
            "camera_id": str(request.data.get("camera_id", "test-camera")),
            "employee_name": request.data.get("employee_name", "Test Employee"),
            "trigger_reason": request.data.get("trigger_reason", "Manual test alert"),
        }

        if settings.ALERT_TEST_TRANSPORT == "zmq":
            send_packet_over_zmq(payload, settings.ZMQ_INGEST_CONNECT_ADDRESS)
            return Response({"queued": True, "event_id": payload["event_id"]}, status=status.HTTP_202_ACCEPTED)

        processed_payload = process_alert_packet(payload)
        return Response(processed_payload, status=status.HTTP_201_CREATED)


class StopRecordingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        event_id = request.data.get("event_id")
        if not event_id:
            raise ValidationError({"event_id": "This field is required."})

        alert = get_object_or_404(Alert, event_id=event_id)
        payload = resolve_alert(
            alert,
            reason=request.data.get("reason", "manager_clear"),
        )
        return Response(payload, status=status.HTTP_200_OK)
   
 
def video_stream(request, video_id):
    conn = psycopg2.connect(
        dbname="tensiondb",
        user="postgres",
        password="capstone",
        host="10.122.96.28",
        port=5432
    )

    cur = conn.cursor()
    cur.execute("SELECT lo_oid FROM video WHERE video_id = %s;", (video_id,))
    lo_oid = cur.fetchone()[0]

    lo = conn.lobject(lo_oid, 'rb')

    def stream():
        try:
            chunk = lo.read(8192)
            while chunk:
                yield chunk
                chunk = lo.read(8192)
        finally:
            lo.close()
            conn.close()

    return StreamingHttpResponse(stream(), content_type="video/mp4")
    
