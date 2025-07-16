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
- [Real-time Features](#real-time-features)
- [Frontend Integration Guide](#frontend-integration-guide)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

Fasticket is a comprehensive event management platform built with Django REST Framework. It provides a complete solution for creating, managing, and selling tickets for events. The platform supports both free and paid events, integrated payment processing via Paystack, automated email notifications, QR code-based ticket validation, and real-time analytics.

## Features

### 🔐 **Authentication & User Management**
- JWT-based authentication with refresh tokens
- OTP verification for registration and password reset
- User profile management with comprehensive data
- Secure password reset functionality
- Public user information access

### 🎪 **Event Management**
- Create, update, and delete events with rich metadata
- Support for both free and paid events
- Multiple ticket types per event with individual pricing
- Event capacity management with real-time availability
- Host information management
- Event banner uploads with cloud storage
- Timezone support for global events

### 🎫 **Advanced Ticket Management**
- **Real-time Availability**: Atomic ticket updates prevent overselling
- **Race Condition Protection**: Database-level locks ensure data integrity
- **Automated Ticket Generation**: QR codes with comprehensive ticket data
- **Ticket Validation System**: QR code scanning for event entry
- **Ticket Transfer Functionality**: Transfer tickets between users
- **Refund Request Handling**: Built-in refund management
- **Check-in System**: Track attendee arrival

### 💳 **Payment Processing**
- Paystack integration for secure payments
- Automated payment verification with webhooks
- Payment status tracking and history
- Oversell protection with transaction rollback
- Frontend redirect after payment completion

### 📧 **Email Notification System**
- **Dual Email Flow for Paid Events**:
  1. Purchase success confirmation
  2. Ticket confirmation with QR code
- **Free Event Registration Emails**:
  1. Registration confirmation
  2. Ticket delivery with QR code
- **Authentication Emails**:
  - Registration OTP verification
  - Password reset OTP
- **Styled HTML Templates**: Professional, responsive email designs

### 📊 **Analytics & Reporting**
- **Real-time Event Analytics**: Live sales tracking
- **Revenue Analytics**: Detailed financial reporting
- **Attendee Management**: Complete attendee lists with check-in status
- **Registration Timeline**: 30-day trend analysis
- **Ticket Type Performance**: Individual ticket type analytics
- **Portfolio Overview**: Multi-event dashboard for creators

### 🔒 **Security Features**
- CORS configuration for cross-origin requests
- JWT token authentication with expiration
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- Atomic database operations

## Project Structure

```
fasticket/
├── Profile/                    # User authentication and profile management
│   ├── models.py              # User profile, OTP models
│   ├── views.py               # Auth endpoints (login, register, profile)
│   ├── serializers.py         # User serializers
│   ├── signals.py             # Auto-profile creation
│   └── permissions.py         # Custom permissions
├── event_management/          # Event creation and management
│   ├── models.py              # Event, Tickets, Hosts models
│   ├── views.py               # Event CRUD + Analytics endpoints
│   ├── serializers.py         # Event serializers
│   └── utils.py               # ID generation utilities
├── ticket_management/         # Ticket lifecycle management
│   ├── models.py              # Ticket models with QR codes
│   ├── views.py               # Ticket operations (check-in, transfer)
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
- Redis (for production caching)

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

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

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
4. Configure webhook URL: `https://yourdomain.com/payments/verify_payment/`

### Storage Settings
The project supports Cloudflare R2 for file storage. Configure the R2 settings in `.env` or use local storage for development.

## API Documentation

### Base URL
```
Production: https://yourdomain.com/
Development: http://localhost:8000/
```

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Response Format
All API responses follow this structure:
```json
{
  "status": "success|error",
  "message": "Human readable message",
  "data": {}, // Response data
  "error": "Error message (if applicable)"
}
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

**Frontend Integration:**
```javascript
const registerUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register/initiate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Show OTP input form
      showOTPForm(userData.email);
    } else {
      // Handle errors
      showError(data.error);
    }
  } catch (error) {
    console.error('Registration failed:', error);
  }
};
```

### 2. Confirm Registration
**Endpoint:** `POST /auth/register/confirm`

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

**Frontend Integration:**
```javascript
const confirmRegistration = async (email, otp) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register/confirm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, otp })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user_id', data.user_id);
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error('Confirmation failed:', error);
  }
};
```

### 3. Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "johndoe",
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

### 4. Token Refresh
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

### 5. Password Reset - Request OTP
**Endpoint:** `POST /auth/reset`

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

### 6. Password Reset - Verify OTP
**Endpoint:** `POST /auth/verify-reset`

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newsecurepassword123"
}
```

---

## 👤 Profile Management Endpoints

### 1. Get User Info (Public)
**Endpoint:** `GET /user/<user_id>`
**Authentication:** Not required

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-15T10:30:00Z",
  "profile": {
    "phone": "+1234567890",
    "company": "Tech Corp",
    "location": "New York",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### 2. Update Profile
**Endpoint:** `PUT /profile/update`
**Authentication:** Required

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "newemail@example.com",
  "phone": "+1234567890",
  "company": "New Tech Corp",
  "location": "San Francisco"
}
```

**Frontend Integration:**
```javascript
const updateProfile = async (profileData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/profile/update`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(profileData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess('Profile updated successfully');
      // Update UI with new data
      updateProfileUI(data.data);
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error('Profile update failed:', error);
  }
};
```

---

## 🎪 Event Management Endpoints

### 1. Create Event
**Endpoint:** `POST /events/create`
**Authentication:** Required

**Request Body (Form Data):**
```javascript
const formData = new FormData();
formData.append('title', 'Tech Conference 2024');
formData.append('description', 'Annual technology conference');
formData.append('banner', bannerFile); // File object
formData.append('timezone', 'America/New_York');
formData.append('start_date', '2024-06-15');
formData.append('start_time', '09:00:00');
formData.append('end_date', '2024-06-15');
formData.append('end_time', '17:00:00');
formData.append('location', 'Convention Center, NYC');
formData.append('event_type', 'In-person');
formData.append('capacity', 500);
formData.append('is_paid', true);
formData.append('tickets', JSON.stringify([
  {
    "ticket_type": "Early Bird",
    "quantity": 100,
    "price": 99.99
  },
  {
    "ticket_type": "Regular",
    "quantity": 300,
    "price": 149.99
  }
]));
formData.append('hosts', JSON.stringify([
  {
    "name": "John Smith",
    "email": "john@techcorp.com",
    "role": "Organizer",
    "social_media": "https://linkedin.com/in/johnsmith"
  }
]));
```

**Frontend Integration:**
```javascript
const createEvent = async (eventData, bannerFile) => {
  const formData = new FormData();
  
  // Add all event fields
  Object.keys(eventData).forEach(key => {
    if (key === 'tickets' || key === 'hosts') {
      formData.append(key, JSON.stringify(eventData[key]));
    } else {
      formData.append(key, eventData[key]);
    }
  });
  
  // Add banner file if provided
  if (bannerFile) {
    formData.append('banner', bannerFile);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/events/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess('Event created successfully!');
      // Redirect to event details or dashboard
      window.location.href = `/events/${data.data.id}`;
    } else {
      showError(data.error || 'Failed to create event');
    }
  } catch (error) {
    console.error('Event creation failed:', error);
  }
};
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
      "tickets": [
        {
          "id": "TKT01",
          "ticket_type": "Early Bird",
          "price": "99.99",
          "quantity": 100,
          "available": 95,
          "sold_count": 5
        }
      ],
      "hosts": [
        {
          "name": "John Smith",
          "email": "john@techcorp.com",
          "role": "Organizer"
        }
      ]
    }
  ]
}
```

**Frontend Integration:**
```javascript
const fetchEvents = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/getAll`);
    const data = await response.json();
    
    if (response.ok) {
      // Display events in UI
      displayEvents(data.data);
    } else {
      showError('Failed to fetch events');
    }
  } catch (error) {
    console.error('Failed to fetch events:', error);
  }
};

const displayEvents = (events) => {
  const eventsContainer = document.getElementById('events-container');
  eventsContainer.innerHTML = events.map(event => `
    <div class="event-card" onclick="viewEvent('${event.id}')">
      <img src="${event.banner || '/default-banner.jpg'}" alt="${event.title}">
      <h3>${event.title}</h3>
      <p>${event.location}</p>
      <p>${new Date(event.start_date).toLocaleDateString()}</p>
      <p>${event.is_paid ? 'Paid Event' : 'Free Event'}</p>
      ${event.tickets.map(ticket => `
        <span class="ticket-availability">
          ${ticket.ticket_type}: ${ticket.available}/${ticket.quantity} available
        </span>
      `).join('')}
    </div>
  `).join('');
};
```

### 3. Get Specific Event
**Endpoint:** `GET /events/get/<event_id>`
**Authentication:** Not required

### 4. Update Event
**Endpoint:** `PUT /events/update/<event_id>`
**Authentication:** Required (Event owner only)

### 5. Delete Event
**Endpoint:** `DELETE /events/delete/<event_id>`
**Authentication:** Required (Event owner only)

### 6. Register for Free Event
**Endpoint:** `POST /events/register-free`
**Authentication:** Not required

**Request Body:**
```json
{
  "event_id": "ABC12345",
  "holder_name": "Jane Doe",
  "holder_email": "jane@example.com",
  "holder_phone": "+1234567890",
  "ticket_type_id": "TKT01"
}
```

**Frontend Integration:**
```javascript
const registerForFreeEvent = async (registrationData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/register-free`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(registrationData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess('Registration successful! Check your email for ticket details.');
      // Show ticket details
      displayTicketInfo(data);
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error('Registration failed:', error);
  }
};
```

---

## 💳 Payment Endpoints

### 1. Initialize Payment
**Endpoint:** `POST /payments/initiate_payment/`
**Authentication:** Not required

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

**Frontend Integration:**
```javascript
const initializePayment = async (paymentData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/payments/initiate_payment/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Redirect to Paystack payment page
      window.location.href = data.authorization_url;
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error('Payment initialization failed:', error);
  }
};

// Handle payment success redirect
const handlePaymentCallback = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const ticketId = urlParams.get('ticket_id');
  const ticketCode = urlParams.get('ticket_code');
  const eventName = urlParams.get('event_name');
  
  if (ticketId) {
    showSuccess(`Payment successful! Your ticket ${ticketCode} for ${eventName} is ready.`);
    // Redirect to ticket view
    window.location.href = `/tickets/${ticketId}`;
  }
};
```

### 2. Payment Verification (Automatic)
**Endpoint:** `GET /payments/verify_payment/?trxref=<reference>`
**Authentication:** Not required

This endpoint is called automatically by Paystack after payment. It redirects to your frontend with success/error parameters.

**Success Redirect:**
```
https://yourfrontend.com/payment/success?ticket_id=12345&ticket_code=ABC123&event_name=Tech Conference&amount=99.99
```

**Error Redirect:**
```
https://yourfrontend.com/payment/error?message=Payment verification failed
```

---

## 🎫 Ticket Management Endpoints

### 1. List User Tickets
**Endpoint:** `GET /api/tickets/`
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
    "holder_name": "John Doe",
    "holder_email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Frontend Integration:**
```javascript
const fetchUserTickets = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    const tickets = await response.json();
    
    if (response.ok) {
      displayTickets(tickets);
    } else {
      showError('Failed to fetch tickets');
    }
  } catch (error) {
    console.error('Failed to fetch tickets:', error);
  }
};

const displayTickets = (tickets) => {
  const ticketsContainer = document.getElementById('tickets-container');
  ticketsContainer.innerHTML = tickets.map(ticket => `
    <div class="ticket-card">
      <h3>${ticket.ticket_type.event.title}</h3>
      <p>Ticket Type: ${ticket.ticket_type.ticket_type}</p>
      <p>Price: ₦${ticket.price}</p>
      <p>Code: ${ticket.ticket_code}</p>
      <p>Status: ${ticket.status}</p>
      <p>Check-in: ${ticket.checked_in ? 'Yes' : 'No'}</p>
      <img src="${ticket.qr_code}" alt="QR Code" class="qr-code">
      <button onclick="viewTicket('${ticket.id}')">View Details</button>
    </div>
  `).join('');
};
```

### 2. Verify Ticket
**Endpoint:** `POST /api/tickets/verify/`
**Authentication:** Required

**Request Body:**
```json
{
  "ticket_code": "ABCD123456"
}
```

### 3. Check-in Ticket
**Endpoint:** `POST /api/tickets/<ticket_id>/check_in/`
**Authentication:** Required

### 4. Transfer Ticket
**Endpoint:** `POST /api/tickets/<ticket_id>/transfer/`
**Authentication:** Required

**Request Body:**
```json
{
  "new_holder_name": "Jane Smith",
  "new_holder_email": "jane@example.com",
  "new_holder_phone": "+0987654321"
}
```

---

## 📊 Analytics & Reporting Endpoints

### 1. Individual Event Analytics
**Endpoint:** `GET /events/analytics/<event_id>`
**Authentication:** Required (Event creator only)

**Response:**
```json
{
  "status": "success",
  "data": {
    "event_info": {
      "event_id": "ABC12345",
      "event_title": "Tech Conference 2024",
      "event_date": "2024-06-15",
      "event_time": "09:00:00",
      "location": "Convention Center, NYC",
      "capacity": 500,
      "is_paid": true
    },
    "summary": {
      "total_tickets_sold": 150,
      "total_tickets_available": 350,
      "total_revenue": 14999.50,
      "total_attendees": 150,
      "checked_in_count": 75,
      "capacity_utilization": 30.0,
      "average_ticket_price": 99.99
    },
    "ticket_types": [
      {
        "ticket_type_id": "TKT01",
        "ticket_type_name": "Early Bird",
        "price": 99.99,
        "total_quantity": 100,
        "sold": 85,
        "available": 15,
        "revenue": 8499.15,
        "sold_percentage": 85.0
      }
    ],
    "revenue_breakdown": {
      "total_revenue": 14999.50,
      "by_ticket_type": {
        "Early Bird": 8499.15,
        "Regular": 6500.35
      }
    },
    "registration_timeline": [
      {
        "date": "2024-01-15",
        "registrations": 25
      }
    ],
    "attendees": [
      {
        "ticket_id": "12345",
        "ticket_code": "ABCD123456",
        "holder_name": "John Doe",
        "holder_email": "john@example.com",
        "ticket_type": "Early Bird",
        "price_paid": 99.99,
        "registration_date": "2024-01-15T10:30:00Z",
        "checked_in": true,
        "check_in_time": "2024-06-15T08:45:00Z",
        "status": "paid"
      }
    ],
    "status_breakdown": {
      "paid": 145,
      "transferred": 5,
      "cancelled": 0,
      "refunded": 0
    }
  }
}
```

**Frontend Integration:**
```javascript
const fetchEventAnalytics = async (eventId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/analytics/${eventId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      displayAnalytics(data.data);
    } else {
      showError(data.error);
    }
  } catch (error) {
    console.error('Failed to fetch analytics:', error);
  }
};

const displayAnalytics = (analytics) => {
  // Update summary cards
  document.getElementById('total-revenue').textContent = `₦${analytics.summary.total_revenue.toLocaleString()}`;
  document.getElementById('total-attendees').textContent = analytics.summary.total_attendees;
  document.getElementById('capacity-utilization').textContent = `${analytics.summary.capacity_utilization}%`;
  
  // Create revenue chart
  createRevenueChart(analytics.revenue_breakdown.by_ticket_type);
  
  // Create registration timeline chart
  createTimelineChart(analytics.registration_timeline);
  
  // Display attendee list
  displayAttendeeList(analytics.attendees);
};
```

### 2. All Events Analytics Dashboard
**Endpoint:** `GET /events/analytics`
**Authentication:** Required

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_events": 5,
      "total_revenue": 45000.00,
      "total_attendees": 450,
      "active_events": 3,
      "past_events": 2
    },
    "events": [
      {
        "event_id": "ABC12345",
        "title": "Tech Conference 2024",
        "date": "2024-06-15",
        "time": "09:00:00",
        "location": "Convention Center, NYC",
        "is_paid": true,
        "attendees": 150,
        "revenue": 14999.50,
        "capacity": 500,
        "tickets_available": 350,
        "tickets_sold": 150,
        "capacity_utilization": 30.0
      }
    ]
  }
}
```

---

## Real-time Features

### 🔄 **Real-time Ticket Availability**

The system implements atomic database operations to ensure real-time ticket availability updates:

```javascript
// Frontend polling for real-time updates
const pollTicketAvailability = (eventId) => {
  setInterval(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/events/get/${eventId}`);
      const data = await response.json();
      
      if (response.ok) {
        updateTicketAvailability(data.data.tickets);
      }
    } catch (error) {
      console.error('Failed to poll ticket availability:', error);
    }
  }, 5000); // Poll every 5 seconds
};

const updateTicketAvailability = (tickets) => {
  tickets.forEach(ticket => {
    const availabilityElement = document.getElementById(`ticket-${ticket.id}-availability`);
    if (availabilityElement) {
      availabilityElement.textContent = `${ticket.available}/${ticket.quantity} available`;
      
      // Update UI based on availability
      if (ticket.available === 0) {
        availabilityElement.classList.add('sold-out');
        document.getElementById(`buy-${ticket.id}`).disabled = true;
      }
    }
  });
};
```

### 📊 **Real-time Analytics Updates**

```javascript
// WebSocket connection for real-time analytics (if implemented)
const connectAnalyticsWebSocket = (eventId) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/analytics/${eventId}/`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateAnalyticsDashboard(data);
  };
};

// Alternative: Polling for analytics updates
const pollAnalytics = (eventId) => {
  setInterval(async () => {
    const analytics = await fetchEventAnalytics(eventId);
    updateAnalyticsDashboard(analytics);
  }, 30000); // Update every 30 seconds
};
```

## Frontend Integration Guide

### 🔧 **Authentication Flow**

```javascript
class AuthService {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async makeAuthenticatedRequest(url, options = {}) {
    // Add authorization header
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    let response = await fetch(url, {
      ...options,
      headers
    });

    // Handle token refresh
    if (response.status === 401 && this.refreshToken) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        response = await fetch(url, {
          ...options,
          headers
        });
      }
    }

    return response;
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: this.refreshToken
        })
      });

      if (response.ok) {
        const data = await response.json();
        this.accessToken = data.access;
        localStorage.setItem('access_token', data.access);
        return true;
      } else {
        // Refresh token expired, redirect to login
        this.logout();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout();
      return false;
    }
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    window.location.href = '/login';
  }
}
```

### 🎫 **Event Management Integration**

```javascript
class EventService {
  constructor(authService) {
    this.auth = authService;
  }

  async createEvent(eventData, bannerFile) {
    const formData = new FormData();
    
    // Add all event fields
    Object.keys(eventData).forEach(key => {
      if (key === 'tickets' || key === 'hosts') {
        formData.append(key, JSON.stringify(eventData[key]));
      } else {
        formData.append(key, eventData[key]);
      }
    });
    
    if (bannerFile) {
      formData.append('banner', bannerFile);
    }

    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/events/create`,
      {
        method: 'POST',
        body: formData,
        headers: {} // Don't set Content-Type for FormData
      }
    );

    return response.json();
  }

  async getEvents() {
    const response = await fetch(`${this.auth.baseURL}/events/getAll`);
    return response.json();
  }

  async getEventAnalytics(eventId) {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/events/analytics/${eventId}`
    );
    return response.json();
  }
}
```

### 💳 **Payment Integration**

```javascript
class PaymentService {
  constructor(authService) {
    this.auth = authService;
  }

  async initializePayment(paymentData) {
    const response = await fetch(`${this.auth.baseURL}/payments/initiate_payment/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData)
    });

    const data = await response.json();
    
    if (response.ok) {
      // Redirect to Paystack
      window.location.href = data.authorization_url;
    } else {
      throw new Error(data.error);
    }
  }

  handlePaymentCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get('ticket_id');
    const ticketCode = urlParams.get('ticket_code');
    const eventName = urlParams.get('event_name');
    const amount = urlParams.get('amount');

    if (ticketId) {
      return {
        success: true,
        ticket: { ticketId, ticketCode, eventName, amount }
      };
    } else {
      const errorMessage = urlParams.get('message');
      return {
        success: false,
        error: errorMessage || 'Payment failed'
      };
    }
  }
}
```

### 📊 **Analytics Dashboard Integration**

```javascript
class AnalyticsService {
  constructor(authService) {
    this.auth = authService;
  }

  async getEventAnalytics(eventId) {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/events/analytics/${eventId}`
    );
    return response.json();
  }

  async getAllEventsAnalytics() {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/events/analytics`
    );
    return response.json();
  }

  createRevenueChart(revenueData) {
    // Using Chart.js or similar library
    const ctx = document.getElementById('revenueChart').getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(revenueData),
        datasets: [{
          data: Object.values(revenueData),
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Revenue by Ticket Type'
          }
        }
      }
    });
  }

  createTimelineChart(timelineData) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: timelineData.map(item => item.date),
        datasets: [{
          label: 'Registrations',
          data: timelineData.map(item => item.registrations),
          borderColor: '#36A2EB',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Registration Timeline (Last 30 Days)'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}
```

### 🎫 **Ticket Management Integration**

```javascript
class TicketService {
  constructor(authService) {
    this.auth = authService;
  }

  async getUserTickets() {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/api/tickets/`
    );
    return response.json();
  }

  async verifyTicket(ticketCode) {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/api/tickets/verify/`,
      {
        method: 'POST',
        body: JSON.stringify({ ticket_code: ticketCode })
      }
    );
    return response.json();
  }

  async checkInTicket(ticketId) {
    const response = await this.auth.makeAuthenticatedRequest(
      `${this.auth.baseURL}/api/tickets/${ticketId}/check_in/`,
      {
        method: 'POST'
      }
    );
    return response.json();
  }

  generateTicketQR(ticketCode) {
    // Using QR code library
    const qr = new QRCode(document.getElementById('qr-container'), {
      text: ticketCode,
      width: 200,
      height: 200
    });
  }
}
```

## Email Templates

The platform includes 5 professionally designed HTML email templates:

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

### Paystack Integration Flow

1. **Initialize Payment:** Frontend calls `/payments/initiate_payment/`
2. **Redirect User:** User completes payment on Paystack
3. **Webhook/Callback:** Paystack calls `/payments/verify_payment/`
4. **Verification:** System verifies payment with Paystack API
5. **Ticket Creation:** Creates ticket and sends confirmation emails
6. **Frontend Redirect:** Redirects to frontend with success/error data

### Frontend Payment Flow

```javascript
// 1. Initialize payment
const paymentData = {
  name: "John Doe",
  email: "john@example.com",
  ticket_type_id: "TKT01"
};

try {
  const response = await fetch('/payments/initiate_payment/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(paymentData)
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Redirect to Paystack
    window.location.href = data.authorization_url;
  }
} catch (error) {
  console.error('Payment initialization failed:', error);
}

// 2. Handle payment callback (on success/error page)
const urlParams = new URLSearchParams(window.location.search);
const ticketId = urlParams.get('ticket_id');

if (ticketId) {
  // Payment successful
  showSuccess('Payment successful! Your ticket is ready.');
} else {
  // Payment failed
  const errorMessage = urlParams.get('message');
  showError(errorMessage || 'Payment failed');
}
```

## Production Deployment

### Environment Variables for Production

```env
# Basic Configuration
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Frontend Configuration
FRONTEND_URL=https://yourdomain.com

# Database Configuration
POSTGRES_DATABASE=fasticket_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432

# Paystack Configuration (Live Keys)
PAYSTACK_SECRET_KEY=sk_live_your_live_secret_key
PAYSTACK_PUBLIC_KEY=pk_live_your_live_public_key

# Email Configuration
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password

# Storage Configuration
CLOUDFLARE_R2_BUCKET=your-production-bucket
CLOUDFLARE_R2_ACCESS_KEY=your_access_key
CLOUDFLARE_R2_SECRET_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your_endpoint.r2.cloudflarestorage.com
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
- [ ] Set up Paystack webhooks
- [ ] Test payment flow end-to-end
- [ ] Configure rate limiting
- [ ] Set up error tracking (Sentry)

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ticket.wsgi:application"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

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
  "error": "Descriptive error message",
  "details": {
    "field": ["Specific field error"]
  }
}
```

### Frontend Error Handling

```javascript
const handleAPIError = (response, data) => {
  switch (response.status) {
    case 400:
      showValidationErrors(data.details);
      break;
    case 401:
      // Redirect to login
      window.location.href = '/login';
      break;
    case 403:
      showError('You do not have permission to perform this action');
      break;
    case 404:
      showError('Resource not found');
      break;
    case 500:
      showError('Server error. Please try again later.');
      break;
    default:
      showError(data.error || 'An unexpected error occurred');
  }
};
```

## Rate Limiting

### API Rate Limits
- **Authentication endpoints:** 5 requests per minute
- **General endpoints:** 100 requests per minute
- **Payment endpoints:** 10 requests per minute

### Frontend Rate Limiting Handling

```javascript
const makeAPIRequest = async (url, options, retries = 3) => {
  try {
    const response = await fetch(url, options);
    
    if (response.status === 429) {
      // Rate limited
      const retryAfter = response.headers.get('Retry-After') || 60;
      
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        return makeAPIRequest(url, options, retries - 1);
      } else {
        throw new Error('Rate limit exceeded. Please try again later.');
      }
    }
    
    return response;
  } catch (error) {
    throw error;
  }
};
```

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test Profile
python manage.py test event_management
python manage.py test payment
python manage.py test ticket_management

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### API Testing Script
Use the provided `test_apis.py` script to test all endpoints:

```bash
python test_apis.py
```

## Contributing

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Ensure backward compatibility

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature: description"

# Push and create pull request
git push origin feature/new-feature
```

## Support

For support and questions:
- **Email:** support@fasticket.com
- **Documentation:** [API Documentation](https://api.fasticket.com/docs)
- **Issues:** [GitHub Issues](https://github.com/your-repo/fasticket/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django REST Framework**

### Quick Start for Frontend Developers

1. **Base URL:** `https://api.yourdomain.com/`
2. **Authentication:** JWT tokens in Authorization header
3. **Content Type:** `application/json` (except file uploads)
4. **Error Handling:** Check response status and handle accordingly
5. **Real-time Updates:** Poll ticket availability every 5-10 seconds
6. **Payment Flow:** Initialize → Redirect → Handle callback
7. **File Uploads:** Use FormData for event creation with banners

### Essential Frontend Libraries
- **HTTP Client:** Axios or Fetch API
- **Charts:** Chart.js or D3.js for analytics
- **QR Codes:** qrcode.js for ticket display
- **Date Handling:** date-fns or moment.js
- **State Management:** Redux, Zustand, or Context API