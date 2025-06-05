from rest_framework import serializers
from .models import *


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['id', 'category', 'image', 'price', 'ticket_code']
        read_only_fields = ['ticket_code', 'qr_code', 'status']

class EventTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventTicket
        fields = '__all__'
