from django.contrib import admin
from .models import Events, Tickets #, TicketCategories

admin.site.register(Events)
# admin.site.register(TicketCategories)
admin.site.register(Tickets)
