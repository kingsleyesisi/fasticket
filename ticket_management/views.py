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
    """
    API viewset for managing generic Tickets.

    Provides standard CRUD operations for Ticket instances.
    Includes a custom action to validate a ticket.

    Permissions: AllowAny (for all actions)

    Allowed HTTP Methods:
        - GET (list, retrieve)
        - POST (create)
        - PUT (update)
        - PATCH (partial_update)
        - DELETE (destroy)
        - GET (validate_ticket - custom action)

    Request/Response Formats:
        - Uses `serializers.TicketSerializer` for request and response data.
    """
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    permission_classes = [AllowAny]

    def send_qr_code_email(self, ticket):
        """
        Sends an email with the ticket QR code attached.
        This is a helper method and not directly exposed as an API endpoint.

        Args:
            ticket (Ticket): The ticket instance for which to send the QR code.
        """
        # Note: `ticket.event_name` and `ticket.user.email` are assumed to exist.
        # These fields are not standard in the base Ticket model shown.
        # This might indicate that this method is intended for a more specific ticket model
        # or that the Ticket model has been customized elsewhere.
        subject = f"Your Ticket for {getattr(ticket, 'event_name', 'Your Event')}"
        message = f"Hello,\n\nYour ticket has been generated successfully. Please find your QR code attached.\n\nTicket Code: {ticket.ticket_code}\n\nThank you for your purchase!"
        recipient_email = getattr(getattr(ticket, 'user', None), 'email', None)

        if not recipient_email:
            # Cannot send email without a recipient
            return

        if ticket.qr_code:
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            qr_code_path = ticket.qr_code.path

            if os.path.exists(qr_code_path):
                email.attach_file(qr_code_path)
            email.send()

    @action(detail=True, methods=['get'], url_path='validate')
    def validate_ticket(self, request, pk=None):
        """
        Custom action to validate a ticket by its ID (pk).

        Allowed HTTP Methods:
            - GET

        Path: `/tickets/{pk}/validate/`

        Response:
            - 200 OK: {'message': 'Ticket is valid', 'ticket': TicketSerializer.data}
            - 404 Not Found: If ticket with the given pk does not exist.
        """
        ticket = get_object_or_404(Ticket, id=pk)
        serializer = self.get_serializer(ticket)
        return Response({'message': 'Ticket is valid', 'ticket': serializer.data})


class EventTicketViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing EventTickets.

    Provides standard CRUD operations for EventTicket instances.

    Permissions: AllowAny (for all actions)

    Allowed HTTP Methods:
        - GET (list, retrieve)
        - POST (create)
        - PUT (update)
        - PATCH (partial_update)
        - DELETE (destroy)

    Request/Response Formats:
        - Uses `serializers.EventTicketSerializer` for request and response data.
    """
    queryset = EventTicket.objects.all()
    serializer_class = serializers.EventTicketSerializer

    permission_classes = [AllowAny]

class HotelTicketViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing HotelTickets.

    Provides standard CRUD operations for HotelTicket instances.

    Permissions: AllowAny (for all actions)

    Allowed HTTP Methods:
        - GET (list, retrieve)
        - POST (create)
        - PUT (update)
        - PATCH (partial_update)
        - DELETE (destroy)

    Request/Response Formats:
        - Uses `serializers.HotelTicketSerializer` for request and response data.
    """
    queryset = HotelTicket.objects.all()
    serializer_class = serializers.HotelTicketSerializer

    permission_classes = [AllowAny]

class TravelTicketViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing TravelTickets.

    Provides standard CRUD operations for TravelTicket instances.

    Permissions: AllowAny (for all actions)

    Allowed HTTP Methods:
        - GET (list, retrieve)
        - POST (create)
        - PUT (update)
        - PATCH (partial_update)
        - DELETE (destroy)

    Request/Response Formats:
        - Uses `serializers.TravelTicketSerializer` for request and response data.
    """
    queryset = TravelTicket.objects.all()
    serializer_class = serializers.TravelTicketSerializer

    permission_classes = [AllowAny]
