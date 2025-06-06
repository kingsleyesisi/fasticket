from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model # Changed from User to get_user_model
from django.utils import timezone
from django.utils.crypto import get_random_string # Added
from event_management.models import Tickets as EventTicketType # Added
from .utils import generate_ticket_id

User = get_user_model() # Added

class Ticket(models.Model):
    """
    Represents a generic ticket which can be for an event.

    Fields:
        id (UUIDField): Unique identifier for the ticket (primary key).
        category (CharField): The category of the ticket (e.g., 'event'').
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
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
        ('transferred', 'Transferred'),
        ('refunded', 'Refunded'),
    ]

    id = models.CharField(max_length=5, primary_key=True, default=generate_ticket_id)  # Changed to CharField for custom ID
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tickets', null=True, blank=True)
    ticket_type = models.ForeignKey(EventTicketType, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchased_tickets")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    ticket_code = models.CharField(max_length=10, unique=True, null=True)
    total_tickets = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    transfer_history = models.JSONField(default=list, blank=True)
    holder_name = models.CharField(max_length=255, null=True)
    holder_email = models.EmailField(null=True)
    holder_phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"{self.category} - {self.ticket_code}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self.generate_ticket_code()
        if self.status == 'paid' and not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_ticket_code(self):
        while True:
            code = get_random_string(10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            if not Ticket.objects.filter(ticket_code=code).exists():
                return code
    
    def generate_qr_code(self):
        qr_data = {
            'ticket_code': self.ticket_code,
            'category': self.category,
            'holder_name': self.holder_name,
            'status': self.status,
        }
        qr = qrcode.make(str(qr_data))
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        self.qr_code.save(f'qr_{self.ticket_code}.png', ContentFile(buffer.getvalue()), save=False)

    def check_in(self):
        if not self.checked_in and self.status == 'paid':
            self.checked_in = True
            self.check_in_time = timezone.now()
            self.save()
            return True
        return False

    def transfer_ticket(self, new_user, new_holder_name, new_holder_email, new_holder_phone):
        if self.status != 'paid':
            return False
        
        transfer_record = {
            'from_user': self.user.id,
            'to_user': new_user.id,
            'transfer_date': timezone.now().isoformat(),
            'previous_holder': self.holder_name,
        }
        
        self.transfer_history.append(transfer_record)
        self.user = new_user
        self.holder_name = new_holder_name
        self.holder_email = new_holder_email
        self.holder_phone = new_holder_phone
        self.status = 'transferred'
        self.save()
        return True

    def request_refund(self):
        if self.status == 'paid' and not self.checked_in:
            self.status = 'refunded'
            self.save()
            return True
        return False

class EventTicket(Ticket):
    LIVE = 'LIVE'
    ONLINE = 'ONLINE'

    EVENT_CHOICES = [
        ('LIVE', 'LIVE'),
        ('ONLINE', 'ONLINE'),
    ]

    max_tickets_per_user = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.id}"
