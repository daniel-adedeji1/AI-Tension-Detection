from django.shortcuts import render
from .models import User
from rest_framework import generics # type: ignore
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore

# Create your views here.
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]