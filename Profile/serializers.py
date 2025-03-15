from rest_framework import serializers
from .models import UserProfile, PasswordResetOTP
from django.contrib.auth.models import User 

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'email', 'first_name', 'last_name', 'company', 'location', 'created_at']



class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)