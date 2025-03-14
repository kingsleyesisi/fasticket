from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.permissions import AllowAny
from .models import *
from . import serializers
import os

# Create your views here.
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    permission_classes = [AllowAny]

    def send_qr_code_email(self, ticket):
        """Send an email with the ticket QR code attached."""
        subject = f"Your Ticket for {ticket.event_name}"
        message = f"Hello,\n\nYour ticket has been generated successfully. Please find your QR code attached.\n\nTicket Code: {ticket.ticket_code}\n\nThank you for your purchase!"
        recipient_email = ticket.user.email
        
        if ticket.qr_code:
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            qr_code_path = ticket.qr_code.path

            # Attach the QR code
            if os.path.exists(qr_code_path):
                email.attach_file(qr_code_path)

            email.send()

    @action(detail=True, methods=['get'], url_path='validate')
    def validate_ticket(self, request, pk=None):
        """
        Custom action to validate a ticket by ticket_code.
        Usage: /main/tickets/{ticket_code}/validate/
        """
        ticket = get_object_or_404(Ticket, id=pk)
        serializer = self.get_serializer(ticket)
        return Response({'message': 'Ticket is valid', 'ticket': serializer.data})


class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = serializers.EventTicketSerializer

    permission_classes = [AllowAny]

class HotelTicketViewSet(viewsets.ModelViewSet):
    queryset = HotelTicket.objects.all()
    serializer_class = serializers.HotelTicketSerializer

    permission_classes = [AllowAny]

class TravelTicketViewSet(viewsets.ModelViewSet):
    queryset = TravelTicket.objects.all()
    serializer_class = serializers.TravelTicketSerializer

    permission_classes = [AllowAny]
