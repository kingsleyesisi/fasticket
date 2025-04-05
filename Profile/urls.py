from django.urls import path
from .views import (CustomAuthToken, InitiateRegistration, RegisterUser, test, ResetPassword, VerifyOTPView)

urlpatterns = [
  path('auth/login', CustomAuthToken.as_view()),
  path('auth/register/initiate', InitiateRegistration.as_view()),
  path('auth/register/confirm', RegisterUser.as_view()),
  path('auth/reset', ResetPassword.as_view()),
  path('auth/verify-reset', VerifyOTPView.as_view()),
  path('checkAuth', test),
]