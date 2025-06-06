import random

def generate_shareable_links(ticket):
    base_url = "http://127.0.0.1:8000/main/tickets" #Change in Production  
    return f"{base_url}/{ticket.id}/"


def generate_ticket_id():
    """
    Generate a unique 5-character alphanumeric ticket ID.
    This function loops until it finds a number that isn't already used as a ticket ID.
    """
    from ticket_management.models import Ticket  # Lazy import to avoid circular import
    while True:
        new_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

        if not Ticket.objects.filter(id=new_id).exists():
            return new_id