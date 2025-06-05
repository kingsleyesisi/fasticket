from rest_framework import serializers
from .models import *

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'category', 'image', 'price', 'ticket_code', 'status',
            'qr_code', 'checked_in', 'check_in_time', 'holder_name',
            'holder_email', 'holder_phone', 'transfer_history'
        ]
        read_only_fields = ['ticket_code', 'qr_code', 'status', 'transfer_history']

class EventTicketSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = EventTicket
        fields = '__all__'
        read_only_fields = ['available_tickets']

class TicketTransferSerializer(serializers.Serializer):
    new_holder_name = serializers.CharField(max_length=255)
    new_holder_email = serializers.EmailField()
    new_holder_phone = serializers.CharField(max_length=20)

class TicketVerificationSerializer(serializers.Serializer):
    ticket_code = serializers.CharField(max_length=10)