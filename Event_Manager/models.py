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

        if not Events.objects.filter(id=new_id).exists():
            return new_id
        
class Events(models.Model):
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
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(blank=True, null=True) 
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100, default="Public")
    capacity = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Hosts(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="hosts")
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=100)
    social_media = models.URLField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.name} - {self.role} - {self.event.title}"
    
class Tickets(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.ticket_type} - {self.event} - {self.event.id}"