from django.urls import path
from . import views

urlpatterns = [
    path("current-user/get/<int:pk>/", views.UserRetrieveAPIView.as_view(), name="current-user"),
    path("alerts/", views.AlertListView.as_view(), name="alert-list"),
    path("alerts/test/", views.TestAlertView.as_view(), name="test-alert"),
]
