#!/usr/bin/env python3
"""
Comprehensive API Test Script for Fasticket Platform
Tests all endpoints with proper request/response handling
"""

import requests
import json
import time
import random
import string
from datetime import datetime, timedelta
import os

class FasticketAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.event_id = None
        self.ticket_type_id = None
        self.ticket_id = None
        self.payment_reference = None
        
        # Test data
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_username = f"testuser_{int(time.time())}"
        self.test_password = "TestPassword123!"
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def make_request(self, method, endpoint, data=None, files=None, headers=None, params=None):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token exists
        if self.access_token and headers is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        elif self.access_token and headers:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers)
                else:
                    response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None

    def test_authentication_apis(self):
        """Test all authentication related APIs"""
        self.log("=" * 60)
        self.log("TESTING AUTHENTICATION APIs")
        self.log("=" * 60)
        
        # 1. Test Registration Initiation
        self.log("1. Testing Registration Initiation...")
        registration_data = {
            "username": self.test_username,
            "password": self.test_password,
            "email": self.test_email,
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "company": "Test Company",
            "location": "Test City"
        }
        
        response = self.make_request("POST", "/auth/register/initiate", registration_data)
        if response and response.status_code == 200:
            self.log("✅ Registration initiation successful")
            self.log(f"Response: {response.json()}")
        else:
            self.log(f"❌ Registration initiation failed: {response.status_code if response else 'No response'}")
            if response:
                self.log(f"Error: {response.text}")
        
        # 2. Test Registration Confirmation (Manual OTP input)
        self.log("\n2. Testing Registration Confirmation...")
        otp = input("Enter the OTP sent to your email: ").strip()
        
        confirm_data = {
            "email": self.test_email,
            "otp": otp
        }
        
        response = self.make_request("POST", "/auth/register/confirm", confirm_data)
        if response and response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            self.user_id = data.get("user_id")
            self.log("✅ Registration confirmation successful")
            self.log(f"User ID: {self.user_id}")
            self.log(f"Access Token: {self.access_token[:50]}...")
        else:
            self.log(f"❌ Registration confirmation failed: {response.status_code if response else 'No response'}")
            if response:
                self.log(f"Error: {response.text}")
        
        # 3. Test Login
        self.log("\n3. Testing Login...")
        login_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            self.log("✅ Login successful")
            self.log(f"New Access Token: {self.access_token[:50]}...")
        else:
            self.log(f"❌ Login failed: {response.status_code if response else 'No response'}")
            if response:
                self.log(f"Error: {response.text}")
        
        # 4. Test Token Refresh
        self.log("\n4. Testing Token Refresh...")
        if self.refresh_token:
            refresh_data = {"refresh": self.refresh_token}
            response = self.make_request("POST", "/auth/token/refresh", refresh_data)
            if response and response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.log("✅ Token refresh successful")
                self.log(f"New Access Token: {self.access_token[:50]}...")
            else:
                self.log(f"❌ Token refresh failed: {response.status_code if response else 'No response'}")
        
        # 5. Test Check Authentication
        self.log("\n5. Testing Check Authentication...")
        response = self.make_request("GET", "/checkAuth")
        if response and response.status_code == 200:
            self.log("✅ Authentication check successful")
            self.log(f"Response: {response.json()}")
        else:
            self.log(f"❌ Authentication check failed: {response.status_code if response else 'No response'}")
        
        # 6. Test Password Reset (Optional)
        test_reset = input("\nDo you want to test password reset? (y/n): ").strip().lower()
        if test_reset == 'y':
            self.log("\n6. Testing Password Reset Request...")
            reset_data = {"email": self.test_email}
            response = self.make_request("POST", "/auth/reset", reset_data)
            if response and response.status_code == 200:
                self.log("✅ Password reset request successful")
                self.log(f"Response: {response.json()}")
                
                # Test OTP verification
                otp = input("Enter the OTP sent for password reset: ").strip()
                new_password = "NewTestPassword123!"
                
                verify_data = {
                    "email": self.test_email,
                    "otp": otp,
                    "new_password": new_password
                }
                
                response = self.make_request("POST", "/auth/verify-reset", verify_data)
                if response and response.status_code == 200:
                    self.log("✅ Password reset verification successful")
                    self.test_password = new_password  # Update password for future tests
                else:
                    self.log(f"❌ Password reset verification failed: {response.status_code if response else 'No response'}")
            else:
                self.log(f"❌ Password reset request failed: {response.status_code if response else 'No response'}")

    def test_profile_apis(self):
        """Test profile management APIs"""
        self.log("\n" + "=" * 60)
        self.log("TESTING PROFILE APIs")
        self.log("=" * 60)
        
        # 1. Test Get User Info (No Auth Required)
        self.log("1. Testing Get User Info...")
        if self.user_id:
            response = self.make_request("GET", f"/user/{self.user_id}", headers={})
            if response and response.status_code == 200:
                self.log("✅ Get user info successful")
                self.log(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                self.log(f"❌ Get user info failed: {response.status_code if response else 'No response'}")
        
        # 2. Test Update Profile
        self.log("\n2. Testing Update Profile...")
        update_data = {
            "first_name": "Updated",
            "last_name": "User",
            "phone": "+9876543210",
            "company": "Updated Company",
            "location": "Updated City"
        }
        
        response = self.make_request("PUT", "/profile/update", update_data)
        if response and response.status_code == 200:
            self.log("✅ Profile update successful")
            self.log(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            self.log(f"❌ Profile update failed: {response.status_code if response else 'No response'}")
            if response:
                self.log(f"Error: {response.text}")

    def test_event_apis(self):
        """Test event management APIs"""
        self.log("\n" + "=" * 60)
        self.log("TESTING EVENT MANAGEMENT APIs")
        self.log("=" * 60)
        
        # 1. Test Create Paid Event
        self.log("1. Testing Create Paid Event...")
        
        # Calculate future dates
        start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        start_time = "10:00:00"
        end_date = start_date
        end_time = "18:00:00"
        
        event_data = {
            "title": "Test Tech Conference 2024",
            "description": "A comprehensive technology conference for testing purposes",
            "timezone": "UTC",
            "start_date": start_date,
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "location": "Test Convention Center",
            "event_type": "In-person",
            "capacity": 100,
            "is_paid": True,
            "tickets": json.dumps([
                {
                    "ticket_type": "Early Bird",
                    "quantity": 50,
                    "price": 99.99
                },
                {
                    "ticket_type": "Regular",
                    "quantity": 50,
                    "price": 149.99
                }
            ]),
            "hosts": json.dumps([
                {
                    "name": "Test Host",
                    "email": "host@test.com",
                    "role": "Organizer",
                    "social_media": "https://linkedin.com/in/testhost"
                }
            ])
        }
        
        response = self.make_request("POST", "/events/create", event_data)
        if response and response.status_code == 200:
            data = response.json()
            self.event_id = data["data"]["id"]
            if data["data"]["tickets"]:
                self.ticket_type_id = data["data"]["tickets"][0]["id"]
            self.log("✅ Paid event creation successful")
            self.log(f"Event ID: {self.event_id}")
            self.log(f"Ticket Type ID: {self.ticket_type_id}")
        else:
            self.log(f"❌ Paid event creation failed: {response.status_code if response else 'No response'}")
            if response:
                self.log(f"Error: {response.text}")
        
        # 2. Test Create Free Event
        self.log("\n2. Testing Create Free Event...")
        free_event_data = {
            "title": "Free Workshop 2024",
            "description": "A free workshop for testing purposes",
            "start_date": start_date,
            "start_time": "14:00:00",
            "end_date": start_date,
            "end_time": "16:00:00",
            "location": "Online",
            "event_type": "Virtual",
            "capacity": 200,
            "is_paid": False
        }
        
        response = self.make_request("POST", "/events/create", free_event_data)
        if response and response.status_code == 200:
            self.log("✅ Free event creation successful")
            free_event_id = response.json()["data"]["id"]
            self.log(f"Free Event ID: {free_event_id}")
        else:
            self.log(f"❌ Free event creation failed: {response.status_code if response else 'No response'}")
        
        # 3. Test Get All Events
        self.log("\n3. Testing Get All Events...")
        response = self.make_request("GET", "/events/getAll", headers={})
        if response and response.status_code == 200:
            events = response.json()["data"]
            self.log(f"✅ Get all events successful - Found {len(events)} events")
            for event in events[:2]:  # Show first 2 events
                self.log(f"Event: {event['title']} (ID: {event['id']})")
        else:
            self.log(f"❌ Get all events failed: {response.status_code if response else 'No response'}")
        
        # 4. Test Get Specific Event
        self.log("\n4. Testing Get Specific Event...")
        if self.event_id:
            response = self.make_request("GET", f"/events/get/{self.event_id}", headers={})
            if response and response.status_code == 200:
                self.log("✅ Get specific event successful")
                event_data = response.json()["data"]
                self.log(f"Event: {event_data['title']}")
                self.log(f"Tickets: {len(event_data.get('tickets', []))}")
            else:
                self.log(f"❌ Get specific event failed: {response.status_code if response else 'No response'}")
        
        # 5. Test Update Event
        self.log("\n5. Testing Update Event...")
        if self.event_id:
            update_data = {
                "title": "Updated Test Tech Conference 2024",
                "description": "Updated description for testing"
            }
            response = self.make_request("PUT", f"/events/update/{self.event_id}", update_data)
            if response and response.status_code == 200:
                self.log("✅ Event update successful")
            else:
                self.log(f"❌ Event update failed: {response.status_code if response else 'No response'}")
        
        # 6. Test Free Event Registration
        self.log("\n6. Testing Free Event Registration...")
        if free_event_id:
            registration_data = {
                "event_id": free_event_id,
                "holder_name": "Test Attendee",
                "holder_email": "attendee@test.com",
                "holder_phone": "+1111111111"
            }
            response = self.make_request("POST", "/events/register-free", registration_data, headers={})
            if response and response.status_code == 200:
                self.log("✅ Free event registration successful")
                self.log(f"Response: {response.json()}")
            else:
                self.log(f"❌ Free event registration failed: {response.status_code if response else 'No response'}")

    def test_payment_apis(self):
        """Test payment related APIs"""
        self.log("\n" + "=" * 60)
        self.log("TESTING PAYMENT APIs")
        self.log("=" * 60)
        
        # 1. Test Initialize Payment
        self.log("1. Testing Initialize Payment...")
        if self.ticket_type_id:
            payment_data = {
                "name": "Test Buyer",
                "email": "buyer@test.com",
                "ticket_type_id": self.ticket_type_id
            }
            
            response = self.make_request("POST", "/payments/initiate_payment/", payment_data, headers={})
            if response and response.status_code == 200:
                data = response.json()
                self.payment_reference = data.get("reference")
                self.log("✅ Payment initialization successful")
                self.log(f"Payment URL: {data.get('authorization_url')}")
                self.log(f"Reference: {self.payment_reference}")
            else:
                self.log(f"❌ Payment initialization failed: {response.status_code if response else 'No response'}")
                if response:
                    self.log(f"Error: {response.text}")
        
        # 2. Test List Payments (Debug endpoint)
        self.log("\n2. Testing List Payments...")
        response = self.make_request("GET", "/payments/list", headers={})
        if response and response.status_code == 200:
            payments = response.json()
            self.log(f"✅ List payments successful - Found {len(payments)} payments")
            for payment in payments[-3:]:  # Show last 3 payments
                self.log(f"Payment: {payment['email']} - ₦{payment['amount']} - Verified: {payment['verified']}")
        else:
            self.log(f"❌ List payments failed: {response.status_code if response else 'No response'}")
        
        # Note: Payment verification is typically handled by Paystack webhook
        self.log("\n📝 Note: Payment verification is handled by Paystack callback")
        self.log("To test payment verification, complete the payment process through Paystack")

    def test_ticket_apis(self):
        """Test ticket management APIs"""
        self.log("\n" + "=" * 60)
        self.log("TESTING TICKET MANAGEMENT APIs")
        self.log("=" * 60)
        
        # 1. Test List User Tickets
        self.log("1. Testing List User Tickets...")
        response = self.make_request("GET", "/api/tickets/")
        if response and response.status_code == 200:
            tickets = response.json()
            self.log(f"✅ List user tickets successful - Found {len(tickets)} tickets")
            if tickets:
                self.ticket_id = tickets[0]["id"]
                self.log(f"First Ticket ID: {self.ticket_id}")
                for ticket in tickets[:2]:  # Show first 2 tickets
                    self.log(f"Ticket: {ticket['ticket_code']} - Status: {ticket['status']}")
        else:
            self.log(f"❌ List user tickets failed: {response.status_code if response else 'No response'}")
        
        # 2. Test Get Specific Ticket
        self.log("\n2. Testing Get Specific Ticket...")
        if self.ticket_id:
            response = self.make_request("GET", f"/api/tickets/{self.ticket_id}/")
            if response and response.status_code == 200:
                ticket = response.json()
                self.log("✅ Get specific ticket successful")
                self.log(f"Ticket Code: {ticket['ticket_code']}")
                self.log(f"Status: {ticket['status']}")
                self.log(f"Holder: {ticket['holder_name']}")
            else:
                self.log(f"❌ Get specific ticket failed: {response.status_code if response else 'No response'}")
        
        # 3. Test Ticket Verification
        self.log("\n3. Testing Ticket Verification...")
        if self.ticket_id:
            # First get a ticket code
            response = self.make_request("GET", f"/api/tickets/{self.ticket_id}/")
            if response and response.status_code == 200:
                ticket_code = response.json()["ticket_code"]
                
                verify_data = {"ticket_code": ticket_code}
                response = self.make_request("POST", "/api/tickets/verify/", verify_data)
                if response and response.status_code == 200:
                    self.log("✅ Ticket verification successful")
                    self.log(f"Response: {response.json()}")
                else:
                    self.log(f"❌ Ticket verification failed: {response.status_code if response else 'No response'}")
        
        # 4. Test Ticket Check-in
        self.log("\n4. Testing Ticket Check-in...")
        if self.ticket_id:
            response = self.make_request("POST", f"/api/tickets/{self.ticket_id}/check_in/")
            if response and response.status_code == 200:
                self.log("✅ Ticket check-in successful")
                self.log(f"Response: {response.json()}")
            else:
                self.log(f"❌ Ticket check-in failed: {response.status_code if response else 'No response'}")
                if response:
                    self.log(f"Error: {response.text}")
        
        # 5. Test Ticket Transfer
        self.log("\n5. Testing Ticket Transfer...")
        if self.ticket_id:
            transfer_data = {
                "new_holder_name": "New Holder",
                "new_holder_email": "newholder@test.com",
                "new_holder_phone": "+2222222222"
            }
            response = self.make_request("POST", f"/api/tickets/{self.ticket_id}/transfer/", transfer_data)
            if response and response.status_code == 200:
                self.log("✅ Ticket transfer successful")
                self.log(f"Response: {response.json()}")
            else:
                self.log(f"❌ Ticket transfer failed: {response.status_code if response else 'No response'}")
                if response:
                    self.log(f"Error: {response.text}")
        
        # 6. Test Request Refund
        self.log("\n6. Testing Request Refund...")
        if self.ticket_id:
            response = self.make_request("POST", f"/api/tickets/{self.ticket_id}/request_refund/")
            if response and response.status_code == 200:
                self.log("✅ Refund request successful")
                self.log(f"Response: {response.json()}")
            else:
                self.log(f"❌ Refund request failed: {response.status_code if response else 'No response'}")
                if response:
                    self.log(f"Error: {response.text}")

    def cleanup_test_data(self):
        """Clean up test data (optional)"""
        self.log("\n" + "=" * 60)
        self.log("CLEANUP (Optional)")
        self.log("=" * 60)
        
        cleanup = input("Do you want to delete the test event? (y/n): ").strip().lower()
        if cleanup == 'y' and self.event_id:
            response = self.make_request("DELETE", f"/events/delete/{self.event_id}")
            if response and response.status_code == 200:
                self.log("✅ Test event deleted successfully")
            else:
                self.log(f"❌ Failed to delete test event: {response.status_code if response else 'No response'}")

    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting Fasticket API Tests")
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Test Email: {self.test_email}")
        self.log(f"Test Username: {self.test_username}")
        
        try:
            # Test all API groups
            self.test_authentication_apis()
            self.test_profile_apis()
            self.test_event_apis()
            self.test_payment_apis()
            self.test_ticket_apis()
            self.cleanup_test_data()
            
            self.log("\n" + "=" * 60)
            self.log("🎉 ALL TESTS COMPLETED!")
            self.log("=" * 60)
            self.log("📊 Test Summary:")
            self.log(f"✅ Authentication APIs: Tested")
            self.log(f"✅ Profile APIs: Tested")
            self.log(f"✅ Event Management APIs: Tested")
            self.log(f"✅ Payment APIs: Tested")
            self.log(f"✅ Ticket Management APIs: Tested")
            
        except KeyboardInterrupt:
            self.log("\n❌ Tests interrupted by user")
        except Exception as e:
            self.log(f"\n❌ Unexpected error: {e}")

def main():
    """Main function to run the tests"""
    print("🎫 Fasticket API Test Suite")
    print("=" * 60)
    
    # Get base URL from user or use default
    base_url = input("Enter API base URL (default: http://127.0.0.1:8000): ").strip()
    if not base_url:
        base_url = "http://127.0.0.1:8000"
    
    # Initialize and run tests
    tester = FasticketAPITester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()