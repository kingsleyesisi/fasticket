from django.shortcuts import render, get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer, TicketSerializer
from .models import Event, Tickets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from ticket_management.models import Ticket as PurchasedTicket
from django.db import transaction
from django.db.models import F
from django.utils import timezone
import json

User = get_user_model()

class CreateEvent(APIView):
    """
    API view to create a new event.

    Authentication: JWTAuthentication
    Permissions: IsAuthenticated
    Parser Classes: MultiPartParser, FormParser, JSONParser

    Allowed HTTP Methods:
        - POST

    Request Body (POST):
        - user (int): Automatically set to the authenticated user's PK.
        - title (str): Title of the event.
        - description (str): Description of the event.
        - banner (file, optional): Banner image for the event.
        - timezone (str, optional): Timezone for the event (default: "UTC").
        - start_date (date): Start date of the event.
        - start_time (time): Start time of the event.
        - end_date (date, optional): End date of the event.
        - end_time (time, optional): End time of the event.
        - location (str, optional): Location of the event.
        - event_type (str, optional): Type of event (default: "In-person").
        - external_link (url, optional): External link for virtual events.
        - capacity (int): Capacity of the event.
        - is_paid (bool, optional): Whether the event is paid (default: False).
        
    Response (POST):
        - 200 OK: {"message": "Event created successfully!", "data": EventSerializer.data}
        - 400 Bad Request: {"error": "Invalid JSON for tickets."} or {"error": "Invalid Json for Host"} or serializer.errors
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk

        if 'tickets' in data and isinstance(data['tickets'], (str, list)):
            if isinstance(data['tickets'], str):
                try:
                    data['tickets'] = json.loads(data['tickets'])
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON for tickets."}, status=status.HTTP_400_BAD_REQUEST)

        if 'hosts' in data and isinstance(data['hosts'], (str, list)):
            if isinstance(data['hosts'], str):
                try:
                    data['hosts'] = json.loads(data['hosts'])
                except json.JSONDecodeError:
                    return Response({'error': "Invalid Json for Host"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            event = serializer.save()
            
            # Auto-create a default free ticket type for free events if no tickets provided
            if not event.is_paid and not event.tickets.exists():
                Tickets.objects.create(
                    event=event,
                    ticket_type="Regular",
                    quantity=event.capacity,
                    price=0.00
                )
                print(f'Auto-created free ticket type for event {event.id}')
            
            print('event created successfully')
            return Response(
                {"message": "Event created successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        print("Serializer Errors:", serializer.errors)  # Debug
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetEvent(APIView):
    """
    API view to retrieve all events.

    Authentication: None
    Permissions: AllowAny

    Allowed HTTP Methods:
        - GET

    Response (GET):
        - 200 OK: {"status": "success", "data": [EventSerializer.data]}
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        data = {"status": "success",
                "data": serializer.data}
        return Response(data)

class GetParticularEvent(APIView):
    """
    API view to retrieve a particular event by its ID.

    Authentication: None
    Permissions: AllowAny

    Allowed HTTP Methods:
        - GET

    Path Parameters:
        - pk (str): The ID of the event to retrieve.

    Response (GET):
        - 200 OK: {"status": "success", "data": EventSerializer.data}
        - 404 Not Found: If event does not exist (handled by get_object_or_404).
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response({"status": "success", "data": serializer.data})

class UpdateEventView(APIView):
    """
    API view to update an existing event.

    Authentication: JWTAuthentication
    Permissions: IsAuthenticated (Only the event creator can update)

    Allowed HTTP Methods:
        - PUT

    Path Parameters:
        - pk (str): The ID of the event to update.

    Request Body (PUT):
        - Same fields as CreateEvent (POST), but all are optional (partial update).

    Response (PUT):
        - 200 OK: {"message": "Event updated successfully!", "data": EventSerializer.data}
        - 400 Bad Request: serializer.errors
        - 403 Forbidden: {"message": "You do not have permission to update this event"}
        - 404 Not Found: If event does not exist.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if request.user.pk != event.user.pk:
            return Response({"message": "You do not have permission to update this event"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Event updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteEvent(APIView):
    """
    API view to delete an existing event.

    Authentication: JWTAuthentication
    Permissions: IsAuthenticated (Only the event creator can delete)

    Allowed HTTP Methods:
        - DELETE

    Path Parameters:
        - pk (str): The ID of the event to delete.

    Response (DELETE):
        - 200 OK: {"message": "Event deleted successfully"}
        - 403 Forbidden: {"error": "You do not have permission to delete this event"}
        - 404 Not Found: If event does not exist.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user.pk != event.user.pk:
            return Response({"error": "You do not have permission to delete this event"}, status=status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)

class RegisterForFreeEvent(APIView):
    """
    API view to register for free events.
    
    Authentication: None (allows both authenticated and guest users)
    Permissions: AllowAny
    
    Allowed HTTP Methods:
        - POST
    
    Request Body (POST):
        - event_id (str): The ID of the event to register for.
        - holder_name (str): Name of the person attending.
        - holder_email (str): Email of the person attending.
        - holder_phone (str, optional): Phone number of the person attending.
        - ticket_type_id (str, optional): Specific ticket type ID (if not provided, uses first available free ticket)
    
    Response (POST):
        - 200 OK: {"message": "Registration successful!", "ticket_id": ticket_id, "ticket_code": ticket_code}
        - 400 Bad Request: Various error messages for validation failures
        - 404 Not Found: If event doesn't exist
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        event_id = request.data.get('event_id')
        holder_name = request.data.get('holder_name')
        holder_email = request.data.get('holder_email')
        holder_phone = request.data.get('holder_phone', '')
        ticket_type_id = request.data.get('ticket_type_id')  # Optional

        # Validate required fields
        if not all([event_id, holder_name, holder_email]):
            return Response({
                'error': 'Please provide event_id, holder_name, and holder_email.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the event
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if event is free
        if event.is_paid:
            return Response({
                'error': 'This is a paid event. Please use the payment endpoint.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Get available free ticket type
                if ticket_type_id:
                    # Use specific ticket type if provided
                    try:
                        ticket_type = Tickets.objects.select_for_update().get(
                            id=ticket_type_id, 
                            event=event,
                            price=0.00
                        )
                    except Tickets.DoesNotExist:
                        return Response({
                            'error': 'Free ticket type not found for this event.'
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    # Auto-select first available free ticket type
                    ticket_type = Tickets.objects.select_for_update().filter(
                        event=event,
                        price=0.00,
                        available__gt=0
                    ).first()
                    
                    if not ticket_type:
                        # Create a default free ticket type if none exists
                        ticket_type = Tickets.objects.create(
                            event=event,
                            ticket_type="Regular",
                            quantity=event.capacity,
                            price=0.00
                        )
                        print(f"Auto-created free ticket type for event {event.id}")

                # Check availability
                if ticket_type.available <= 0:
                    return Response({
                        'error': 'This event is fully booked.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Decrement available tickets
                ticket_type.available = F('available') - 1
                ticket_type.save(update_fields=['available'])
                ticket_type.refresh_from_db()

                # Get user if authenticated
                user = request.user if request.user.is_authenticated else None

                # Create the purchased ticket
                purchased_ticket = PurchasedTicket.objects.create(
                    user=user,
                    ticket_type=ticket_type,
                    category='event',
                    price=0.00,  # Free ticket
                    status='paid',  # Set as paid since it's free
                    holder_name=holder_name,
                    holder_email=holder_email,
                    holder_phone=holder_phone,
                )

                # Send registration confirmation email
                try:
                    self._send_registration_email(purchased_ticket, event, ticket_type)
                    print(f"Registration confirmation email sent to {holder_email}")
                except Exception as e:
                    print(f"Failed to send registration email to {holder_email}: {e}")

                # Send ticket confirmation email
                try:
                    self._send_ticket_confirmation_email(purchased_ticket, event, ticket_type)
                    print(f"Ticket confirmation email sent to {holder_email}")
                except Exception as e:
                    print(f"Failed to send ticket confirmation email to {holder_email}: {e}")

                return Response({
                    "message": "Registration successful!",
                    "ticket_id": purchased_ticket.id,
                    "ticket_code": purchased_ticket.ticket_code,
                    "event_name": event.title,
                    "ticket_type": ticket_type.ticket_type,
                    "is_free": True
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error during free event registration: {e}")
            return Response({
                'error': 'An unexpected error occurred during registration. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_registration_email(self, ticket, event, ticket_type):
        """Send registration confirmation email for free events."""
        email_context = {
            'registration_details': {
                'name': ticket.holder_name,
                'event_name': event.title,
                'ticket_type': ticket_type.ticket_type,
                'registration_date': timezone.now().strftime('%B %d, %Y at %I:%M %p'),
                'event_date': event.start_date.strftime('%B %d, %Y'),
                'event_time': event.start_time.strftime('%I:%M %p'),
                'event_location': event.location,
            }
        }
        
        subject = f"Registration Successful - {event.title}"
        html_message = render_to_string('emails/free_event_registration_email.html', email_context)
        
        plain_message = (
            f"Hello {ticket.holder_name},\n\n"
            f"Congratulations! You have successfully registered for {event.title}.\n"
            f"Event Date: {event.start_date.strftime('%B %d, %Y')}\n"
            f"Event Time: {event.start_time.strftime('%I:%M %p')}\n"
            f"Location: {event.location or 'TBA'}\n\n"
            f"Your ticket confirmation will be sent separately.\n\n"
            f"Thank you,\nThe Fastickets Team"
        )
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.holder_email],
            html_message=html_message,
            fail_silently=False
        )

    def _send_ticket_confirmation_email(self, ticket, event, ticket_type):
        """Send ticket confirmation email with QR code."""
        email_context = {
            'ticket_details': {
                'event_name': event.title,
                'ticket_type': ticket_type.ticket_type,
                'price': ticket.price,
                'ticket_code': ticket.ticket_code,
                'ticket_id': ticket.id,
                'holder_name': ticket.holder_name,
                'holder_email': ticket.holder_email,
                'event_date': event.start_date.strftime('%B %d, %Y'),
                'event_time': event.start_time.strftime('%I:%M %p'),
                'event_location': event.location,
                'is_free': True,
            },
            'event_banner_url': event.banner.url if event.banner else None,
            'qr_code_url': ticket.qr_code.url if ticket.qr_code else None,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        subject = f"Your Ticket for {event.title}"
        html_message = render_to_string('emails/enhanced_ticket_confirmation_email.html', email_context)
        
        plain_message = (
            f"Hello {ticket.holder_name},\n\n"
            f"Here's your ticket for {event.title}:\n"
            f"Ticket Code: {ticket.ticket_code}\n"
            f"Event Date: {event.start_date.strftime('%B %d, %Y')}\n"
            f"Event Time: {event.start_time.strftime('%I:%M %p')}\n"
            f"Location: {event.location or 'TBA'}\n\n"
            f"Please bring this ticket code for entry.\n\n"
            f"Thank you,\nThe Fastickets Team"
        )
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.holder_email],
            html_message=html_message,
            fail_silently=False
        )

def CreateView(request):
    """
    Renders a simple HTML form for creating an event.
    Likely used for testing or simple admin interactions directly via browser.

    Allowed HTTP Methods:
        - GET

    Response (GET):
        - Renders 'form.html' template.
    """
    return render(request, 'form.html', status=200)