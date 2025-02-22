from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

urlpatterns = [
    path('create', views.CreateEvent.as_view(), name='create'),
    path('update/<int:pk>', views.UpdateEventView.as_view(), name='update'),
    path('delete/<int:pk>', views.DeleteEvent.as_view(), name='delete'),
    path('get', views.GetEvent.as_view(), name='list'),
    path('view', views.CreateView, name='view'),
    path('ticket', views.TicketCategoriesView.as_view(), name='ticket'),
    path('create_tick', views.TicketViewSet.as_view({'post': 'list'}), name='views')
]
