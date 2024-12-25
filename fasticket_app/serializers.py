from rest_framework import serializers
from .models import UserProfile, EventsInfo

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'email', 'first_name', 'last_name', 'company', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsInfo
        fields = ['id', 'title', 'description', 'location', 'date', 'time', 'photo', 'created_at', 'updated_at', 'user']
