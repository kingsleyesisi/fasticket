from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import generate_shareable_links


# Create your models here.
class Ticket(models.Model):
    """
    Represents a generic ticket which can be for an event, hotel, or travel.

    Fields:
        id (UUIDField): Unique identifier for the ticket (primary key).
        category (CharField): The category of the ticket (e.g., 'event', 'hotel', 'travel').
        image (ImageField): An optional image associated with the ticket.
        price (DecimalField): The price of the ticket.
        ticket_code (CharField): A unique code for the ticket (generated automatically).
        total_tickets (PositiveIntegerField): The number of available tickets of this type.
        status (CharField): The status of the ticket (e.g., 'pending', 'paid', 'cancelled').
        qr_code (ImageField): A QR code generated for the ticket when its status is 'paid'.
        created_at (DateTimeField): The date and time when the ticket was created.
        updated_at (DateTimeField): The date and time when the ticket was last updated.
    """
    CATEGORY_CHOICES = [
        ('event', 'Event'),
        ('hotel', 'Hotel'),
        ('travel', 'Travel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    ticket_code = models.CharField(max_length=10, unique=True, null=True)
    total_tickets = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self.generate_ticket_code()
        if self.status == 'paid':  # Generate QR only after payment
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def generate_ticket_code(self):
        import uuid
        return str(uuid.uuid4())[:10]
    
    def generate_qr_code(self):
        qr = qrcode.make(self.ticket_code)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        self.qr_code.save(f'qr_{self.ticket_code}.png', ContentFile(buffer.getvalue()), save=False)

    @action(detail=True, methods=['get'])
    def share(self, request, pk=None):
        """
        Custom action to share a ticket by ticket_id.
        Usage: /main/tickets/<id>/share/
        """
        ticket = self.get_object()
        shareable_link = generate_shareable_links(ticket)
        return Response({"shareable_link": shareable_link})
    

class EventTicket(Ticket):
    """
    Represents a ticket specifically for an event, inheriting from the base Ticket model.

    Fields:
        title (CharField): The title of the event.
        description (TextField): A description of the event.
        event_date (DateTimeField): The date and time of the event.
        choice (CharField): The type of event (e.g., 'LIVE', 'ONLINE').
        start_date (DateTimeField): The start date and time of the event (can be same as event_date).
        end_date (DateTimeField): The end date and time of the event.
    """
    LIVE = 'LIVE'
    ONLINE = 'ONLINE'

    EVENT_CHOICES = [
        ('LIVE','LIVE'),
        ('ONLINE','ONLINE'),
    ]

    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    event_date = models.DateTimeField()
    choice = models.CharField(max_length=6, choices=EVENT_CHOICES, default=LIVE)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.id}"
    

class HotelTicket(Ticket):
    """
    Represents a ticket specifically for a hotel booking, inheriting from the base Ticket model.

    Fields:
        name (CharField): The name of the hotel.
        description (TextField): A description of the hotel or booking details.
        check_in (DateField): The check-in date for the hotel booking.
        check_out (DateField): The check-out date for the hotel booking.
    """
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f"{self.id}"

class TravelTicket(Ticket):
    """
    Represents a ticket specifically for travel, inheriting from the base Ticket model.
    This model is currently a placeholder and can be extended with travel-specific fields.
    """
    pass
