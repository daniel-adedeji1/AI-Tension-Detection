from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from .models import User
from rest_framework import generics, status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .serializers import UserSerializer, UserCreateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.authentication import BaseAuthentication # type: ignore
from rest_framework.exceptions import AuthenticationFailed # type: ignore


class CustomSessionAuthentication(BaseAuthentication):
    """Custom session authentication for custom User model"""
    def authenticate(self, request):
        employee_id = request.session.get('employee_id')
        
        if not employee_id:
            return None
        
        try:
            user = User.objects.get(employee_id=employee_id)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        password = request.data.get('e_password')

        if not employee_id or not password:
            return Response(
                {'error': 'Employee ID and Password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verify password against hashed password
        if not check_password(password, user.e_password_hash):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Create session
        request.session['employee_id'] = user.employee_id
        request.session.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Clear session
        request.session.flush()
        return Response(status=status.HTTP_200_OK)