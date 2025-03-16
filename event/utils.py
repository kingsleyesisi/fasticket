def generate_shareable_links(ticket):
    base_url = "http://127.0.0.1:8000/main/tickets" #Change in Production  
    return f"{base_url}/{ticket.id}/"