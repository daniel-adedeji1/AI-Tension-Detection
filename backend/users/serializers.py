from .models import User
from rest_framework import serializers # type: ignore
from django.contrib.auth.hashers import make_password

class UserCreateSerializer(serializers.ModelSerializer):
    e_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('e_first_name','e_last_name', 'e_phone', 'e_email', 'e_password', 'role')
    
    def create(self, validated_data):
        password = validated_data.pop('e_password')
        hashed_password = make_password(password)
        user = User.objects.create(
            e_first_name=validated_data['e_first_name'],
            e_last_name=validated_data['e_last_name'],
            e_password_hash=hashed_password,
            e_email=validated_data.get('e_email', ''),
            e_phone=validated_data.get('e_phone', ''),
            role=validated_data['role'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('employee_id', 'e_first_name','e_last_name', 'e_phone', 'e_email', 'e_password_hash', 'role')
        read_only_fields = ('employee_id', 'e_password_hash')
        