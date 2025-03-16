from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
import datetime
from django.utils import timezone

# Userprofile Model
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
class RegistrationOTP(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=128)  # Plaintext for demo; see note below
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if OTP is still valid (30 minutes)."""
        if self.created_at is None:
            return False
        return (timezone.now() - self.created_at).seconds < 1800 # 30 minutes validity
    
    def __str__(self):
        return f"registration OTP for {self.email}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).seconds < 1800  # 30 minutes validity
    
    def __str__(self):
        return f"OTP for {self.user.username}"