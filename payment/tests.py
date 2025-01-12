import requests_mock
from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.sites.models import Site
from .paystack import Paystack

class PaystackTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.paystack = Paystack()
        self.email = 'test@example.com'
        self.amount = 10000  # Amount in kobo (100 NGN)
        self.site = Site.objects.get_current()

    @requests_mock.Mocker()
    def test_pay(self, mock):
        # Mock the Paystack API response
        mock.post(f'{self.paystack.base_url}/transaction/initialize', json={
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://paystack.com/pay/testurl",
                "access_code": "ACCESS_CODE",
                "reference": "REFERENCE"
            }
        })

        # Create a mock request
        request = self.factory.get('/')
        request.site = self.site

        # Call the Pay method
        response = self.paystack.Pay(self.email, self.amount, request=request)

        # Check the response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://paystack.com/pay/testurl")