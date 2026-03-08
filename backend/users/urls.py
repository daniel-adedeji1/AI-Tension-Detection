from django.urls import path
from . import views

urlpatterns = [
    path("current-user/get/<int:pk>/", views.UserRetrieveAPIView.as_view(), name="current-user"),
]