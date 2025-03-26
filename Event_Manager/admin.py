from django.contrib import admin
from .models import Events, Tickets, Hosts #, TicketCategories

admin.site.register(Events)
# admin.site.register(TicketCategories)
admin.site.register(Tickets)
admin.site.register(Hosts)
