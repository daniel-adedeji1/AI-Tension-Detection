from .models import User
from rest_framework import serializers # type: ignore

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'username', 'password', 'email', 'phone', 'is_manager')
        extra_kwargs = { 'password': {'write_only': True} }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            is_manager=validated_data['is_manager']
        )
        return user
        