from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Events(models.Model):
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", blank=True, null=True)
    Hosts = models.CharField(blank=True, max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to="event_banners/")
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    ticket_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Tickets(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="ticket_categories")
    name = models.CharField(max_length=100, default="Regular")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # seat_capacity = models.ForeignKey(Events, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.name} - {self.event.title}"