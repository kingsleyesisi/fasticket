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

2.  **User Authentication:**

    *   **Register:** `POST /auth/register/initiate` and `POST /auth/register/confirm` to create a new user.
    *   **Login:** `POST /auth/login` to obtain an authentication token.
    *   Include the token in the `Authorization` header for protected endpoints.

3.  **Event Management:**

    *   **Create Event:** `POST /events/create` to create a new event.
    *   **Get All Events:** `GET /events/getAll` to retrieve all events.
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
