# Fasticket: Event Management Platform 🚀

## Description

Fasticket is a comprehensive platform designed to streamline event management, from creation to ticket sales. Whether you're organizing a small meetup or a large conference, Fasticket provides the tools you need to manage events efficiently. Our platform offers features for user authentication, event creation, payment processing, and much more, all built with Django and a RESTful API.

## Key Features 🌟

*   **User Authentication**: Secure user registration, login, and profile management.
*   **Event Creation & Management**: Easily create, update, and delete events with detailed information like date, time, location, and capacity.
*   **Ticket Management**: Define multiple ticket types and manage their availability and pricing.
*   **Payment Integration**: Seamless payment processing via Paystack for secure ticket purchases.
*   **RESTful API**: A powerful API for managing events and tickets programmatically.
*   **Email Verification:** Sends email to newly registered user
*   **Password Reset:** Sends an OTP to registered user to reset password

## Project Structure 🏗️

The project is organized into the following Django apps:

*   **`Profile`**: Handles user authentication (registration, login, OTP verification, password reset) and user profile management.
*   **`event_management`**: Manages the creation, updating, deletion, and retrieval of events. It also handles event-specific details like hosts and ticket types (distinct from the general ticket management).
*   **`ticket_management`**: Deals with the lifecycle of different kinds of tickets (e.g., event tickets, hotel tickets, travel tickets), including their creation, validation, and sharing.
*   **`payment`**: Integrates with Paystack to process payments for tickets.

## Installation 🔧

Follow these steps to get Fasticket up and running on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**

    *   On Windows:

        ```bash
        .venv\Scripts\activate
        ```

    *   On macOS and Linux:

        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure environment variables:**

    *   Create a `.env` file in the project root directory.
    *   Add the following environment variables:

        ```
        DEBUG=True
        PAYSTACK_SECRET_KEY=<your_paystack_secret_key>
        PAYSTACK_PUBLIC_KEY=<your_paystack_public_key>
        EMAIL_HOST=<your_email_host>
        EMAIL_PORT=<your_email_port>
        EMAIL_USE_TLS=<True/False>
        EMAIL_HOST_USER=<your_email_host_user>
        EMAIL_HOST_PASSWORD=<your_email_host_password>
        ```

6.  **Apply migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7.  **Create a superuser (optional):**

    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the server:**

    ```bash
    python manage.py runserver
    ```

## Usage 💻

1.  **Access the API:**

    *   The API endpoints are available at `http://localhost:8000/`.
    *   Use tools like Postman or `curl` to interact with the API or any API testing tools of your choice.

2.  **User Authentication (`/auth/`)**

    *   **Register:**
        *   `POST /auth/register/initiate`: Initiates the registration process and sends an OTP.
            *   Example Body: `{"username": "newuser", "password": "password123", "email": "user@example.com", "first_name": "Test", "last_name": "User", "phone": "1234567890"}`
        *   `POST /auth/register/confirm`: Confirms registration with the OTP.
            *   Example Body: `{"email": "user@example.com", "otp": "123456"}`
    *   **Login:** `POST /auth/login`: Logs in an existing user and returns an auth token.
        *   Example Body: `{"username": "testuser", "password": "password123"}` or `{"email": "user@example.com", "password": "password123"}`
    *   **Password Reset:**
        *   `POST /auth/reset`: Initiates password reset by sending an OTP. (Corresponds to `ResetPassword` view)
            *   Example Body: `{"email": "user@example.com"}`
        *   `POST /auth/verify-reset`: Verifies OTP and sets a new password. (Corresponds to `VerifyOTPView` view)
            *   Example Body: `{"email": "user@example.com", "otp": "123456", "new_password": "newsecurepassword"}`
    *   **Check Authentication:** `GET /checkAuth`: A test endpoint to verify if the token is valid. (Requires Authorization token)


3.  **Event Management (`/events/`)**

    *   **Create Event:** `POST /events/create`: Creates a new event. (Requires Authorization token)
        *   Example Body: `{"title": "My Awesome Event", "description": "Join us!", "start_date": "2024-12-01", "start_time": "10:00:00", "capacity": 100, "is_paid": true, "tickets": [{"ticket_type": "General", "quantity": 50, "price": 25.00}]}`
    *   **Get All Events:** `GET /events/getAll`: Retrieves a list of all events.
    *   **Get Specific Event:** `GET /events/get/<event_id>`: Retrieves details of a specific event by its ID.
    *   **Update Event:** `PUT /events/update/<event_id>`: Updates an existing event. (Requires Authorization token, user must be event owner)
    *   **Delete Event:** `DELETE /events/delete/<event_id>`: Deletes an event. (Requires Authorization token, user must be event owner)
    *   **View Event Creation Form (Test):** `GET /events/view`: Renders an HTML form for creating an event (primarily for testing/dev).


4.  **Ticket Management (`/main/`)**

    This app manages different types of tickets. Endpoints are usually prefixed with `/main/`.
    *   **Generic Tickets (`/main/tickets/`)**:
        *   List/Create: `GET /main/tickets/`, `POST /main/tickets/`
        *   Retrieve/Update/Delete: `GET /main/tickets/<ticket_id>/`, `PUT /main/tickets/<ticket_id>/`, `DELETE /main/tickets/<ticket_id>/`
        *   Validate Ticket: `GET /main/tickets/<ticket_id>/validate/`
        *   Share Ticket: `GET /main/tickets/<ticket_id>/share/` (Note: This is defined in the model but might not be directly exposed via a URL unless explicitly routed in `ticket_management/urls.py`)
    *   **Event Tickets (`/main/event/`)**:
        *   List/Create: `GET /main/event/`, `POST /main/event/`
        *   Retrieve/Update/Delete: `GET /main/event/<ticket_id>/`, `PUT /main/event/<ticket_id>/`, `DELETE /main/event/<ticket_id>/`

5.  **Payment (`/payments/`)**

    *   **Initiate Payment:** `POST /payments/initiate_payment/`: Initiates payment for an event/ticket.
        *   Example Body: `{"email": "user@example.com", "amount": 2500, "eventID": "event_id_123"}` (Amount is in smallest currency unit, e.g., kobo for NGN)
    *   **Verify Payment:** `GET /payments/verify_payment/<reference>`: Verifies the payment status using the reference from Paystack. The actual callback URL configured on Paystack might differ but will likely trigger a view that uses this logic.

## API Endpoints (Legacy - for reference, might be outdated)

The following information might be outdated due to recent refactoring. Please refer to the code or updated sections above.

3.  **Event Management:**

    *   **Create Event:** `POST /events/create` to create a new event.
    *   **Get All Events:** `GET /events/getAll` to retrieve all events. (Note: Model name changed from Events to Event)
    *   **Get Event:** `GET /events/get/<pk>` to retrieve a specific event by ID.
    *   **Update Event:** `PUT /events/update/<pk>` to update an existing event.
    *   **Delete Event:** `DELETE /events/delete/<pk>` to delete an event.

4.  **Payment:**

    *   **Initiate Payment:** `POST /payments/initiate_payment/` to initiate payment.
    *   **Verify Payment:** Configure the callback URL to `payments/verify_payment/` to verify payment.
5.  **View Form:**

     *   **Create Event**: `GET /events/view` To view the form for testing purposes


## Contributing 🤝

We welcome contributions to Fasticket! Here's how you can contribute:

1.  **Fork the repository.**
2.  **Create a new branch:**

    ```bash
    git checkout -b feature/your-feature
    ```

3.  **Make your changes and commit them:**

    ```bash
    git add .
    git commit -m "Add your descriptive commit message"
    ```

4.  **Push to the branch:**

    ```bash
    git push origin feature/your-feature
    ```

5.  **Submit a pull request.**

## License
