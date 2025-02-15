from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

urlpatterns = [
    path('get', views.CreateEventView.as_view(), name='get'),
    path('create', views.CreateEvent.as_view(), name='create')
    path('get', views.GetEvent.as_view(), name='list'),
]
