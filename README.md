# Fasticket

Fasticket is a ticketing system built with Django REST Framework (DRF).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication and authorization
- Event creation and management
- Support for multiple ticket statuses
- RESTful API for ticket operations
- Detailed event and ticket information
- User-friendly interface

## Installation

To get started with Fasticket, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/kingsleyesisi/fasticket.git
    cd fasticket
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the migration and start the development server:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

## Configuration

Configure the application by setting the necessary environment variables in a `.env` file in the root directory. 
Example:
   SECRET_KEY=your_secret_key
   DEBUG=True
   PAYSTACK_SECRET=sk_12345678


## API Documentation

The Fasticket API provides endpoints for managing events and tickets. Below are some of the main endpoints:

- **User Registration and Authentication**
    - `POST /api/register/` - Register a new user
    - `POST /api/login/` - Login a user
    - `POST /api/logout/` - Logout a user

- **Event Management**
    - `GET /api/events/` - List all events
    - `POST /api/events/` - Create a new event
    - `GET /api/events/:id/` - Retrieve a specific event
    - `PUT /api/events/:id/` - Update an event
    - `DELETE /api/events/:id/` - Delete an event

- **Ticket Management**
    - `GET /api/tickets/` - List all tickets
    - `POST /api/tickets/` - Create a new ticket
    - `GET /api/tickets/:id/` - Retrieve a specific ticket
    - `PUT /api/tickets/:id/` - Update a ticket
    - `DELETE /api/tickets/:id/` - Delete a ticket

## Usage

After setting up the project, you can access the application at `http://127.0.0.1:8000/`. Use the provided API endpoints to interact with the system.

## Project Structure

Here is an overview of the project structure:
   fasticket/ ├── fasticket/ │ ├── init.py │ ├── settings.py │ ├── urls.py │ ├── wsgi.py ├── events/ │ ├── init.py │ ├── admin.py │ ├── apps.py │ ├── models.py │ ├── serializers.py │ ├── urls.py │ ├── views.py ├── tickets/ │ ├── init.py │ ├── admin.py │ ├── apps.py │ ├── models.py │ ├── serializers.py │ ├── urls.py │ ├── views.py ├── manage.py └── requirements.txt

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
