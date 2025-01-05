from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .paystack import Paystack

class Payments(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    reference = models.CharField(max_length=255, unique=False)
    email = models.EmailField()
    eventID = models.CharField(max_length=200, blank=True, null=True)
    Verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} paid {self.amount}"

    def save(self, *args, **kwargs):
        paystack = Paystack()
        status, data_or_message = paystack.verify_payment(self.reference)

        if status == True:
            self.paid_at = timezone.now()
            self.Verified = True
            super(Payments, self).save(*args, **kwargs)
        else:
            self.Verified = False
            super(Payments, self).save(*args, **kwargs)

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.reference, self.amount)
        if status == True:
            self.Verified = True
            self.save()
        if self.Verified:
          return True
        return False