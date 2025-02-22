from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Events(models.Model):
    # id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", blank=True, null=True)
    Hosts = models.CharField(blank=True, max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to="event_banners/")
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)
    # ticket_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class TicketCategories(models.Model):
    CATEGORY_CHOICES = [
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('vvip', 'VVIP'),
        ('other', 'Other'),
    ]
    
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name='ticket_categories')
    ticket_type = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField()

    def __str__(self):
        return self.ticket_type
class Tickets(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="Ticket")
    category = models.ForeignKey(TicketCategories, on_delete=models.CASCADE, related_name='tickets')
    quantity = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # seat_capacity = models.ForeignKey(Events, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if self.category.available_tickets >= self.quantity:
            self.category.available_tickets -= self.quantity
            self.category.save()
        else:
            raise ValueError("Not enough tickets available")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} {self.category.ticket_type} ticket(s) for {self.event.title}"
    