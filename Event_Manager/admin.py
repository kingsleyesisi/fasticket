from django.contrib import admin
from .models import Events, Tickets

admin.site.register(Events)
# admin.site.register(TicketCategory)
admin.site.register(Tickets)
