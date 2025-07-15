from django.urls import path
from .views import (CustomTokenObtainPairView, UpdateProfile, InitiateRegistration, RegisterUser, test, ResetPassword, VerifyOTPView, GetUserInfo)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
  path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
  path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),


  path('auth/register/initiate', InitiateRegistration.as_view()),
  path('auth/register/confirm', RegisterUser.as_view()),
  path('auth/reset', ResetPassword.as_view()),
  path('profile/update', UpdateProfile.as_view(), name='update_profile'),
  path('user/<int:user_id>', GetUserInfo.as_view(), name='get_user_info'),
  path('auth/verify-reset', VerifyOTPView.as_view()),
  path('checkAuth', test),
]
