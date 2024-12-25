from django.urls import path
from . import views
from .views import CustomAuthToken, RegisterUser

urlpatterns = [
  path('auth/login', CustomAuthToken.as_view()),
  path('auth/register', RegisterUser.as_view()),

]