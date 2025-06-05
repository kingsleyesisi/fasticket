import uuid
from django.db import models
from django.contrib.auth import get_user_model
import random

User = get_user_model()

def generate_unique_event_id():
    """
    Generate a unique 8-digit string. This function loops until it finds a number
    that isn’t already used as an event ID.
    """
    while True:
        new_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=8))

        if not Event.objects.filter(id=new_id).exists():
            return new_id

class Event(models.Model):
    """
    Represents an event created by a user.

    Fields:
        id (CharField): Unique 8-character alphanumeric ID for the event (primary key).
        user (ForeignKey): The user who created the event.
        title (CharField): The title of the event.
        description (TextField): A detailed description of the event.
        banner (ImageField): An optional banner image for the event.
        timezone (CharField): The timezone of the event (e.g., "UTC", "America/New_York").
        start_date (DateField): The starting date of the event.
        start_time (TimeField): The starting time of the event.
        end_date (DateField): The ending date of the event (optional).
        end_time (TimeField): The ending time of the event (optional).
        location (CharField): The physical location of the event (if applicable).
        event_type (CharField): The type of event (e.g., "In-person", "Virtual", "Hybrid").
        external_link (URLField): A URL for virtual events.
        capacity (PositiveIntegerField): The maximum number of attendees for the event.
        is_paid (BooleanField): Whether the event requires paid tickets.
        date_created (DateTimeField): The date and time when the event was created.
    """
    id = models.CharField(
        editable=False,
        primary_key=True,
        max_length=8,
        default=generate_unique_event_id,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to="event_banners/", blank=True)
    timezone = models.CharField(max_length=100, null=True, default="UTC")
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(null=True)
    end_time = models.TimeField(null=True)
    location = models.CharField(max_length=255, blank=True) # Physical location
    event_type = models.CharField(max_length=100, default="In-person") # In-person, Virtual, Hybrid
    external_link = models.URLField(blank=True) # For virtual events
    capacity = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Hosts(models.Model):
    """
    Represents a host or organizer for an event.

    Fields:
        event (ForeignKey): The event to which this host is associated.
        name (CharField): The name of the host.
        email (EmailField): The email address of the host (optional).
        role (CharField): The role of the host (e.g., "Organizer", "Speaker").
        social_media (URLField): A link to the host's social media profile (optional).
        phone (CharField): The phone number of the host (optional).
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="hosts")
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=100)
    social_media = models.URLField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.name} - {self.role} - {self.event.title}"

class Tickets(models.Model):
    """
    Represents a type of ticket available for an event.

    Fields:
        event (ForeignKey): The event for which this ticket type is available.
        ticket_type (CharField): The name or type of the ticket (e.g., "Regular", "VIP").
        quantity (PositiveIntegerField): The number of tickets available for this type.
        price (DecimalField): The price of one ticket of this type.
        available (PositiveIntegerField): The number of tickets avaialble (by default it is the quantity of tickets)
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    available = models.PositiveIntegerField(default=0)  # Default value set to 0
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.ticket_type} - {self.event} - {self.event.id}"
    
    def save(self, *args, **kwargs):
        # Only set available on creation if it wasn't provided
        if self._state.adding and self.available == 0:
            self.available = self.quantity
        super().save(*args, **kwargs)
