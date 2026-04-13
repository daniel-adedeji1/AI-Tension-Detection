from django.urls import path, include
from users.views import UserCreateView, LoginView, LogoutView

urlpatterns = [
    path('api/users/register/', UserCreateView.as_view(), name='register'),
    path('api/users/login/', LoginView.as_view(), name='login'),
    path('api/users/logout/', LogoutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/users/', include('users.urls')),
]
