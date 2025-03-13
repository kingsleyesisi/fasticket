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
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f"{self.id}"

class TravelTicket(Ticket):
    pass
