# Fasticket: Event Management Platform 🎫

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Email Templates](#email-templates)
- [Payment Integration](#payment-integration)
- [Contributing](#contributing)
- [License](#license)

## Overview

Fasticket is a comprehensive event management platform built with Django REST Framework. It provides a complete solution for creating, managing, and selling tickets for events. The platform supports both free and paid events, integrated payment processing via Paystack, automated email notifications, and QR code-based ticket validation.

## Features

### 🔐 **Authentication & User Management**
- JWT-based authentication
- OTP verification for registration and password reset
- User profile management
- Secure password reset functionality

### 🎪 **Event Management**
- Create, update, and delete events
- Support for both free and paid events
- Multiple ticket types per event
- Event capacity management
- Host information management
- Event banner uploads

### 🎫 **Ticket Management**
- Automated ticket generation
- QR code generation with comprehensive ticket data
- Ticket validation and check-in system
- Ticket transfer functionality
- Refund request handling

### 💳 **Payment Processing**
- Paystack integration for secure payments
- Automated payment verification
- Payment status tracking
- Oversell protection

### 📧 **Email Notifications**
- Registration confirmation emails
- Purchase success notifications
- Ticket confirmation with QR codes
- Styled HTML email templates
- Password reset emails

### 🔒 **Security Features**
- CORS configuration
- JWT token authentication
- Rate limiting
- Input validation and sanitization

## Project Structure

```
fasticket/
├── Profile/                    # User authentication and profile management
│   ├── models.py              # User profile, OTP models
│   ├── views.py               # Auth endpoints
│   ├── serializers.py         # User serializers
│   └── permissions.py         # Custom permissions
├── event_management/          # Event creation and management
│   ├── models.py              # Event, Tickets, Hosts models
│   ├── views.py               # Event CRUD operations
│   ├── serializers.py         # Event serializers
│   └── utils.py               # ID generation utilities
├── ticket_management/         # Ticket lifecycle management
│   ├── models.py              # Ticket models with QR codes
│   ├── views.py               # Ticket operations
│   ├── serializers.py         # Ticket serializers
│   └── utils.py               # Ticket utilities
├── payment/                   # Payment processing
│   ├── models.py              # Payment records
│   ├── views.py               # Payment endpoints
│   ├── paystack.py            # Paystack integration
│   └── urls.py                # Payment routes
├── helper/                    # Utility modules
│   └── cloudflare/            # Cloudflare R2 storage
├── templates/                 # Email templates
│   └── emails/                # HTML email templates
└── ticket/                    # Main Django project
    ├── settings.py            # Project configuration
    └── urls.py                # Main URL routing
```

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1+
- PostgreSQL/MySQL (optional, SQLite for development)

### Setup Instructions

1. **Clone the repository:**
```bash
git clone <repository_url>
cd fasticket
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment configuration:**
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key

# Database (optional - defaults to SQLite)
POSTGRES_DATABASE=fasticket_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Paystack Configuration
PAYSTACK_SECRET_KEY=sk_test_your_secret_key
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Cloudflare R2 Storage (optional)
CLOUDFLARE_R2_BUCKET=your_bucket_name
CLOUDFLARE_R2_ACCESS_KEY=your_access_key
CLOUDFLARE_R2_SECRET_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your_endpoint.r2.cloudflarestorage.com
```

5. **Database setup:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional
```

6. **Run the server:**
```bash
python manage.py runserver
```

## Configuration

### Email Settings
Configure SMTP settings in your `.env` file. For Gmail:
- Use App Passwords instead of regular passwords
- Enable 2-factor authentication
- Generate an App Password for the application

### Payment Settings
1. Create a Paystack account at [paystack.com](https://paystack.com)
2. Get your test/live API keys from the dashboard
3. Add keys to your `.env` file

### Storage Settings
The project supports Cloudflare R2 for file storage. Configure the R2 settings in `.env` or use local storage for development.

## API Documentation

### Base URL
```
http://localhost:8000/
```

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### 1. Initiate Registration
**Endpoint:** `POST /auth/register/initiate`

**Description:** Starts the registration process by sending an OTP to the user's email.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "location": "New York"
}
```

**Response:**
```json
{
  "message": "OTP sent to your email. Please verify to complete registration."
}
```

**Error Responses:**
```json
{
  "error": "Please provide all required fields"
}
```
```json
{
  "error": "Username already exists"
}
```
```json
{
  "error": "Email already exists"
}
```

### 2. Confirm Registration
**Endpoint:** `POST /auth/register/confirm`

**Description:** Completes registration by verifying the OTP.

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Error Responses:**
```json
{
  "error": "Please provide both email and OTP"
}
```
```json
{
  "error": "Invalid OTP or email"
}
```
```json
{
  "error": "OTP has expired"
}
```

### 3. Login
**Endpoint:** `POST /auth/login`

**Description:** Authenticates user and returns JWT tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```
**OR**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

### 4. Password Reset - Request OTP
**Endpoint:** `POST /auth/reset`

**Description:** Sends OTP for password reset.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully"
}
```

### 5. Password Reset - Verify OTP
**Endpoint:** `POST /auth/verify-reset`

**Description:** Verifies OTP and sets new password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newsecurepassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successful",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 6. Token Refresh
**Endpoint:** `POST /auth/token/refresh`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🎪 Event Management Endpoints

### 1. Create Event
**Endpoint:** `POST /events/create`
**Authentication:** Required

**Description:** Creates a new event with optional tickets and hosts.

**Request Body (Form Data):**
```json
{
  "title": "Tech Conference 2024",
  "description": "Annual technology conference featuring industry leaders",
  "banner": "<file>",
  "timezone": "America/New_York",
  "start_date": "2024-06-15",
  "start_time": "09:00:00",
  "end_date": "2024-06-15",
  "end_time": "17:00:00",
  "location": "Convention Center, NYC",
  "event_type": "In-person",
  "external_link": "",
  "capacity": 500,
  "is_paid": true,
  "tickets": "[{\"ticket_type\": \"Early Bird\", \"quantity\": 100, \"price\": 99.99}, {\"ticket_type\": \"Regular\", \"quantity\": 300, \"price\": 149.99}]",
  "hosts": "[{\"name\": \"John Smith\", \"email\": \"john@techcorp.com\", \"role\": \"Organizer\", \"social_media\": \"https://linkedin.com/in/johnsmith\"}]"
}
```

**Response:**
```json
{
  "message": "Event created successfully!",
  "data": {
    "id": "ABC12345",
    "user": 1,
    "title": "Tech Conference 2024",
    "description": "Annual technology conference featuring industry leaders",
    "banner": "https://storage.example.com/event_banners/banner.jpg",
    "timezone": "America/New_York",
    "start_date": "2024-06-15",
    "start_time": "09:00:00",
    "end_date": "2024-06-15",
    "end_time": "17:00:00",
    "location": "Convention Center, NYC",
    "event_type": "In-person",
    "external_link": "",
    "capacity": 500,
    "is_paid": true,
    "date_created": "2024-01-15T10:30:00Z",
    "tickets": [
      {
        "id": "TKT01",
        "ticket_type": "Early Bird",
        "price": "99.99",
        "quantity": 100,
        "available": 100
      },
      {
        "id": "TKT02",
        "ticket_type": "Regular",
        "price": "149.99",
        "quantity": 300,
        "available": 300
      }
    ],
    "hosts": [
      {
        "name": "John Smith",
        "email": "john@techcorp.com",
        "role": "Organizer",
        "social_media": "https://linkedin.com/in/johnsmith"
      }
    ]
  }
}
```

### 2. Get All Events
**Endpoint:** `GET /events/getAll`
**Authentication:** Not required

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "ABC12345",
      "title": "Tech Conference 2024",
      "description": "Annual technology conference",
      "banner": "https://storage.example.com/event_banners/banner.jpg",
      "start_date": "2024-06-15",
      "start_time": "09:00:00",
      "location": "Convention Center, NYC",
      "capacity": 500,
      "is_paid": true,
      "tickets": [...],
      "hosts": [...]
    }
  ]
}
```

### 3. Get Specific Event
**Endpoint:** `GET /events/get/<event_id>`
**Authentication:** Not required

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "ABC12345",
    "title": "Tech Conference 2024",
    "description": "Annual technology conference featuring industry leaders",
    "banner": "https://storage.example.com/event_banners/banner.jpg",
    "timezone": "America/New_York",
    "start_date": "2024-06-15",
    "start_time": "09:00:00",
    "end_date": "2024-06-15",
    "end_time": "17:00:00",
    "location": "Convention Center, NYC",
    "event_type": "In-person",
    "capacity": 500,
    "is_paid": true,
    "tickets": [
      {
        "id": "TKT01",
        "ticket_type": "Early Bird",
        "price": "99.99",
        "quantity": 100,
        "available": 95
      }
    ],
    "hosts": [
      {
        "name": "John Smith",
        "email": "john@techcorp.com",
        "role": "Organizer",
        "social_media": "https://linkedin.com/in/johnsmith"
      }
    ]
  }
}
```

### 4. Update Event
**Endpoint:** `PUT /events/update/<event_id>`
**Authentication:** Required (Event owner only)

**Request Body:** Same as create event (all fields optional for partial update)

**Response:**
```json
{
  "message": "Event updated successfully!",
  "data": {
    // Updated event data
  }
}
```

### 5. Delete Event
**Endpoint:** `DELETE /events/delete/<event_id>`
**Authentication:** Required (Event owner only)

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

### 6. Register for Free Event
**Endpoint:** `POST /events/register-free`
**Authentication:** Not required

**Description:** Register for a free event without payment.

**Request Body:**
```json
{
  "event_id": "ABC12345",
  "holder_name": "Jane Doe",
  "holder_email": "jane@example.com",
  "holder_phone": "+1234567890"
}
```

**Response:**
```json
{
  "message": "Registration successful!",
  "ticket_id": "12345",
  "ticket_code": "ABCD123456",
  "event_name": "Free Workshop",
  "ticket_type": "General Admission",
  "is_free": true
}
```

**Error Responses:**
```json
{
  "error": "Please provide event_id, holder_name, and holder_email."
}
```
```json
{
  "error": "Event not found."
}
```
```json
{
  "error": "This is a paid event. Please use the payment endpoint."
}
```
```json
{
  "error": "This event is fully booked."
}
```

---

## 💳 Payment Endpoints

### 1. Initialize Payment
**Endpoint:** `POST /payments/initiate_payment/`
**Authentication:** Not required

**Description:** Initializes payment for a paid event ticket.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "ticket_type_id": "TKT01"
}
```

**Response:**
```json
{
  "authorization_url": "https://checkout.paystack.com/abc123",
  "access_code": "abc123def456",
  "reference": "ref_abc123def456"
}
```

**Error Responses:**
```json
{
  "error": "Please provide an email."
}
```
```json
{
  "error": "Please provide ticket_type_id."
}
```
```json
{
  "error": "Invalid ticket_type_id."
}
```
```json
{
  "error": "This ticket type is sold out."
}
```

### 2. Payment Verification (Callback)
**Endpoint:** `GET /payments/verify_payment/?trxref=<reference>`
**Authentication:** Not required

**Description:** Automatically called by Paystack after payment. Verifies payment and creates ticket.

**Response (Success):**
```json
{
  "data": "success",
  "message": "Payment verified and ticket created successfully.",
  "ticket_id": "12345",
  "ticket_code": "ABCD123456"
}
```

**Response (Already Verified):**
```json
{
  "data": "success",
  "message": "Payment already verified."
}
```

**Response (Oversold):**
```json
{
  "error": "Tickets are sold out. Your payment was successful but no ticket could be issued. Please contact support.",
  "data": "oversold"
}
```

### 3. List Payments (Debug)
**Endpoint:** `GET /payments/list`
**Authentication:** Not required

**Response:**
```json
[
  {
    "reference": "ref_abc123",
    "amount": 99.99,
    "email": "john@example.com",
    "verified": true
  }
]
```

---

## 🎫 Ticket Management Endpoints

### 1. List User Tickets
**Endpoint:** `GET /main/tickets/`
**Authentication:** Required

**Response:**
```json
[
  {
    "id": "12345",
    "user": 1,
    "ticket_type": {
      "id": "TKT01",
      "ticket_type": "Early Bird",
      "price": "99.99",
      "event": {
        "id": "ABC12345",
        "title": "Tech Conference 2024"
      }
    },
    "category": "event",
    "price": "99.99",
    "ticket_code": "ABCD123456",
    "status": "paid",
    "qr_code": "https://storage.example.com/qr_codes/qr_ABCD123456.png",
    "checked_in": false,
    "holder_name": "John Doe",
    "holder_email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 2. Get Specific Ticket
**Endpoint:** `GET /main/tickets/<ticket_id>/`
**Authentication:** Required

**Response:**
```json
{
  "id": "12345",
  "user": 1,
  "ticket_type": {
    "id": "TKT01",
    "ticket_type": "Early Bird",
    "price": "99.99",
    "event": {
      "id": "ABC12345",
      "title": "Tech Conference 2024",
      "start_date": "2024-06-15",
      "start_time": "09:00:00",
      "location": "Convention Center, NYC"
    }
  },
  "category": "event",
  "price": "99.99",
  "ticket_code": "ABCD123456",
  "status": "paid",
  "qr_code": "https://storage.example.com/qr_codes/qr_ABCD123456.png",
  "checked_in": false,
  "check_in_time": null,
  "holder_name": "John Doe",
  "holder_email": "john@example.com",
  "holder_phone": "+1234567890",
  "transfer_history": [],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Check-in Ticket
**Endpoint:** `POST /main/tickets/<ticket_id>/check_in/`
**Authentication:** Required

**Response:**
```json
{
  "message": "Check-in successful"
}
```

**Error Response:**
```json
{
  "error": "Check-in failed. Ticket may be invalid or already used."
}
```

### 4. Transfer Ticket
**Endpoint:** `POST /main/tickets/<ticket_id>/transfer/`
**Authentication:** Required

**Request Body:**
```json
{
  "new_holder_name": "Jane Smith",
  "new_holder_email": "jane@example.com",
  "new_holder_phone": "+0987654321"
}
```

**Response:**
```json
{
  "message": "Ticket transferred successfully"
}
```

### 5. Request Refund
**Endpoint:** `POST /main/tickets/<ticket_id>/request_refund/`
**Authentication:** Required

**Response:**
```json
{
  "message": "Refund request submitted successfully"
}
```

### 6. Verify Ticket
**Endpoint:** `POST /main/tickets/verify/`
**Authentication:** Required

**Request Body:**
```json
{
  "ticket_code": "ABCD123456"
}
```

**Response:**
```json
{
  "valid": true,
  "ticket": {
    "id": "12345",
    "ticket_code": "ABCD123456",
    "status": "paid",
    "checked_in": false,
    "holder_name": "John Doe",
    "event": "Tech Conference 2024"
  }
}
```

---

## 👤 Profile Management Endpoints

### 1. Update Profile
**Endpoint:** `PUT /profile/update`
**Authentication:** Required

**Request Body:**
```json
{
  "phone": "+1234567890",
  "company": "New Tech Corp",
  "location": "San Francisco"
}
```

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "phone": "+1234567890",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company": "New Tech Corp",
  "location": "San Francisco",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Check Authentication
**Endpoint:** `GET /checkAuth`
**Authentication:** Required

**Response:**
```json
{
  "message": "Access granted"
}
```

---

## Email Templates

The platform includes professionally designed HTML email templates:

### 1. Registration OTP Email
- **Template:** `templates/emails/registration_mail.html`
- **Sent when:** User initiates registration
- **Contains:** 6-digit OTP code with 30-minute validity

### 2. Password Reset Email
- **Template:** `templates/emails/reset_password.html`
- **Sent when:** User requests password reset
- **Contains:** 6-digit OTP code for password reset

### 3. Free Event Registration Email
- **Template:** `templates/emails/free_event_registration_email.html`
- **Sent when:** User registers for free event
- **Contains:** Registration confirmation with event details

### 4. Purchase Success Email
- **Template:** `templates/emails/purchase_success_email.html`
- **Sent when:** Payment is successfully processed
- **Contains:** Payment confirmation with reference number

### 5. Enhanced Ticket Confirmation Email
- **Template:** `templates/emails/enhanced_ticket_confirmation_email.html`
- **Sent when:** Ticket is generated (both free and paid)
- **Contains:** 
  - Ticket details with QR code
  - Event information
  - Entry instructions
  - Ticket ID and code

## Payment Integration

### Paystack Integration
The platform uses Paystack for payment processing:

1. **Initialize Payment:** Creates payment session with Paystack
2. **Redirect User:** User completes payment on Paystack
3. **Webhook/Callback:** Paystack notifies our system
4. **Verification:** System verifies payment with Paystack API
5. **Ticket Creation:** Creates ticket and sends confirmation emails

### Security Features
- Payment verification before ticket creation
- Oversell protection with database transactions
- Secure webhook handling
- Payment reference tracking

## Error Handling

### Common HTTP Status Codes
- **200 OK:** Request successful
- **201 Created:** Resource created successfully
- **400 Bad Request:** Invalid request data
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Permission denied
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

### Error Response Format
```json
{
  "error": "Descriptive error message"
}
```

## Rate Limiting

- **User endpoints:** 10 requests per minute
- **Authentication endpoints:** Protected by Django's built-in throttling
- **Payment endpoints:** No specific limits (handled by Paystack)

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## Deployment

### Environment Variables for Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key

# Database
POSTGRES_DATABASE=fasticket_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432

# Paystack (Live Keys)
PAYSTACK_SECRET_KEY=sk_live_your_live_secret_key
PAYSTACK_PUBLIC_KEY=pk_live_your_live_public_key

# Email (Production SMTP)
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password

# Storage
CLOUDFLARE_R2_BUCKET=your-production-bucket
```

### Deployment Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up production email service
- [ ] Configure static file serving
- [ ] Set up SSL certificate
- [ ] Configure domain and CORS settings
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages
- Ensure backward compatibility

## Support

For support and questions:
- **Email:** support@fasticket.com
- **Documentation:** [API Documentation](https://api.fasticket.com/docs)
- **Issues:** [GitHub Issues](https://github.com/your-repo/fasticket/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django REST Framework**