from rest_framework import serializers
from django.contrib.auth import get_user_model
from oauth2_provider.models import get_application_model

from .models import UserFile
# Application = get_application_model()
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'address',
                  'profile_picture']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'profile_picture']
        read_only_fields = ['username', 'email']

class UserFileSerializer(serializers.ModelSerializer):
    """
    User file serializer.
    """

    class Meta:
        model = UserFile
        fields = ['id', 'user', 'file', 'created_at']