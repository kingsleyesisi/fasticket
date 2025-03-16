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

class HotelTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = HotelTicket
        fields = ['id', 'category', 'name', 'description', 'image', 'price', 'ticket_code', 'qr_code', 'status']
        read_only_fields = ['check_in', 'check_out']


class TravelTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelTicket
        fields = '__all__'
