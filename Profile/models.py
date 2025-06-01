from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
import datetime
from django.utils import timezone

# Userprofile Model
class UserProfile(models.Model):
    """
    Represents the profile for a user, extending the built-in User model.

    Fields:
        user (ForeignKey): A one-to-one link to Django's User model.
        company (CharField): The company the user works for (optional).
        phone (CharField): The user's phone number.
        location (CharField): The user's location.
        created_at (DateTimeField): The date and time when the profile was created.
        updated_at (DateTimeField): The date and time when the profile was last updated.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class RegistrationOTP(models.Model):
    """
    Stores OTP (One-Time Password) data for user registration verification.
    This model temporarily holds user registration details until OTP verification.

    Fields:
        username (CharField): The desired username for the new user.
        email (EmailField): The email address for the new user.
        first_name (CharField): The first name of the new user.
        last_name (CharField): The last name of the new user.
        phone (CharField): The phone number of the new user.
        company (CharField): The company of the new user (optional).
        location (CharField): The location of the new user (optional).
        password (CharField): The hashed password for the new user.
        otp (CharField): The 6-digit OTP sent to the user's email.
        created_at (DateTimeField): The timestamp when the OTP was generated.
    """
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=128)  # Stores hashed password
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
    """
    Stores OTP (One-Time Password) data for password reset verification.

    Fields:
        user (ForeignKey): The user requesting the password reset.
        otp (CharField): The 6-digit OTP sent to the user's email.
        created_at (DateTimeField): The timestamp when the OTP was generated.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """
        Checks if the OTP is still valid (within a 30-minute window).

        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).seconds < 1800  # 30 minutes validity

    def __str__(self):
        return f"OTP for {self.user.username}"