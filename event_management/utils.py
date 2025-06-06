import random 
# from event_management.models import Event, Tickets

def generate_unique_event_id():
    """
    Generate a unique 8-digit string. This function loops until it finds a number
    that isn't already used as an event ID.
    """
    from event_management.models import Event  # Lazy import to avoid circular import
    while True:
        new_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=8))

        if not Event.objects.filter(id=new_id).exists():
            return new_id
        

def generate_ticket_id():
    """
    Generate a unique 5-character alphanumeric ticket ID.
    This function loops until it finds a number that isn’t already used as a ticket ID.
    """
    from event_management.models import Tickets  # Lazy import to avoid circular import
    while True:
        new_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

        if not Tickets.objects.filter(id=new_id).exists():
            return new_id
        