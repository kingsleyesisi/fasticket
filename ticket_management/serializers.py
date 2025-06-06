from rest_framework import serializers
from .models import *

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'ticket_type', # Added ticket_type, also ensure 'user' is present
            'category', 'image', 'price', 'ticket_code', 'status',
            'qr_code', 'checked_in', 'check_in_time', 'holder_name',
            'holder_email', 'holder_phone', 'transfer_history',
            'created_at', 'updated_at' # It's good practice to include timestamps
        ]
        read_only_fields = ['ticket_code', 'qr_code', 'status', 'transfer_history', 'ticket_type', 'user', 'created_at', 'updated_at']

class EventTicketSerializer(serializers.ModelSerializer):
    # is_available = serializers.BooleanField(read_only=True) # Removed
    
    class Meta:
        model = EventTicket
        fields = '__all__' # This will include fields from Ticket parent class
        read_only_fields = [
            'ticket_code', 'qr_code', 'status', 'transfer_history', 'ticket_type', 'user', # Inherited and should be read-only
            'created_at', 'updated_at' # Inherited timestamps
            # any other fields specific to EventTicket that should be read-only
        ]

class TicketTransferSerializer(serializers.Serializer):
    new_holder_name = serializers.CharField(max_length=255)
    new_holder_email = serializers.EmailField()
    new_holder_phone = serializers.CharField(max_length=20)

class TicketVerificationSerializer(serializers.Serializer):
    ticket_code = serializers.CharField(max_length=10)