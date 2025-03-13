from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'event', EventTicketViewSet)
router.register(r'hotel', HotelTicketViewSet)
router.register(r'travel', TravelTicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]