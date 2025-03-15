from django.urls import path
from .views import (CustomAuthToken, RegisterUser, test, RequestOTPView, VerifyOTPView)

urlpatterns = [
  path('auth/login', CustomAuthToken.as_view()),
  path('auth/register', RegisterUser.as_view()),
  path('auth/request-otp', RequestOTPView.as_view()),
  path('auth/verify-otp', VerifyOTPView.as_view()),
  path('checkAuth', test),
]