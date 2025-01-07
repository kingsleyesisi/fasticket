from rest_framework import serializers
from .models import UserProfile, EventsInfo

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'email', 'first_name', 'last_name', 'company', 'created_at']