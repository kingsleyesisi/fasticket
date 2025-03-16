from django.contrib import admin
from .models import UserProfile, PasswordResetOTP, RegistrationOTP
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(PasswordResetOTP)
admin.site.register(RegistrationOTP)