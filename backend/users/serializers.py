from .models import User
from rest_framework import serializers # type: ignore
from django.contrib.auth.hashers import make_password

class UserCreateSerializer(serializers.ModelSerializer):
    e_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('e_firstname','e_lastname', 'e_phone', 'e_email', 'e_password', 'is_manager')
    
    def create(self, validated_data):
        password = validated_data.pop('e_password')
        hashed_password = make_password(password)
        user = User.objects.create(
            e_firstname=validated_data['e_firstname'],
            e_lastname=validated_data['e_lastname'],
            e_password_hash=hashed_password,
            e_email=validated_data.get('e_email', ''),
            e_phone=validated_data.get('e_phone', ''),
            is_manager=validated_data['is_manager'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('employee_id', 'e_firstname','e_lastname', 'e_phone', 'e_email', 'e_password_hash', 'is_manager')
        read_only_fields = ('employee_id', 'e_password_hash')
        