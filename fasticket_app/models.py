from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.

# Userprofile Model
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    company = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"  
    
    def get_short_name(self):
        return self.user.first_name
    



# This is for all the events  that will be created
" Ask for the information needed to host an event"
class EventsInfo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    photo = models.ImageField(upload_to='media/')
    expected_guests = models.IntegerField()
    

    class TicketGrade(models.TextChoices):
      VIP = 'VIP', _('VIP')
      REGULAR = 'REGULAR', _('Regular')
      ECONOMY = 'ECONOMY', _('Economy')

    grade = models.CharField(
      max_length=10,
      choices=TicketGrade.choices,
      default=TicketGrade.REGULAR,
    )
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
  