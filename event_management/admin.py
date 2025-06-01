from django.contrib import admin
from .models import Event, Tickets, Hosts #, TicketCategories

admin.site.register(Event)
# admin.site.register(TicketCategories)
admin.site.register(Tickets)
admin.site.register(Hosts)
