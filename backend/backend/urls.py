from django.urls import path, include
from users.views import UserCreateView, LoginView, LogoutView, StopRecordingView, video_stream #, VideoListAPIView

urlpatterns = [
    path('api/users/register/', UserCreateView.as_view(), name='register'),
    path('api/users/login/', LoginView.as_view(), name='login'),
    path('api/users/logout/', LogoutView.as_view(), name='logout'),
    path('api/recordings/stop/', StopRecordingView.as_view(), name='stop-recording'),
    path('api/videos/<int:video_id>/', video_stream, name='video-stream'),
    #path('api/videos/', VideoListAPIView.as_view(), name='video-list'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/users/', include('users.urls')),
]
