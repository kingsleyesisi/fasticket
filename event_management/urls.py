from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

urlpatterns = [
    path('create', views.CreateEvent.as_view(), name='create'),
    path('update/<str:pk>', views.UpdateEventView.as_view(), name='update'),
    path('delete/<str:pk>', views.DeleteEvent.as_view(), name='delete'),
    path('getAll', views.GetEvent.as_view(), name='get_all'), # Get all events
    path('get/<str:pk>', views.GetParticularEvent.as_view(), name='get'),
    path('register-free', views.RegisterForFreeEvent.as_view(), name='register_free'),
    path('analytics/<str:event_id>', views.EventAnalyticsView.as_view(), name='event_analytics'),
    path('analytics', views.EventListAnalyticsView.as_view(), name='events_analytics'),
    path('view', views.CreateView, name='view'),
]