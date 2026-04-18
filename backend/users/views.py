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
from .authentication import CustomSessionAuthentication

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
    