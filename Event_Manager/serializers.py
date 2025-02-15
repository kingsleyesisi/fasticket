from rest_framework import serializers
from .models import Events, Tickets

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = '__all__'
