from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Event(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to="event_banners/")
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_categories")
    name = models.CharField(max_length=100, default="Regular")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seat_capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.event.title}"
