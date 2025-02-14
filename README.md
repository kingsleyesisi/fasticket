# Fasticket

Fasticket is a ticketing system built with Django REST Framework (DRF).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [License](#license)

## Features

- User authentication and authorization
- Event creation and management
- Support for multiple ticket statuses
- RESTful API for ticket operations

## Installation

To get started with Fasticket, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kingsleyesisi/fasticket.git
   cd fasticket

2. **Crate a virtual environment and activate it:**
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate
   
   
4. **Install the dependencies:**
     `pip install -r requirements`
   
5. **Run the migration and start development server**
     ```bash
     python manage.py makemigration
     python manage.py migrate
     python manage.py runserver

