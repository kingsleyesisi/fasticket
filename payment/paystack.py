import requests 
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect 
from django.contrib.sites.shortcuts import get_current_site
import json


class Paystack:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.publick_key = settings.PAYSTACK_PUBLIC_KEY
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.paystack.co'

    def Pay(self, email, amount, eventID, **kwargs):
      email = email
      amount = amount * 100 # convert from kobo to Naira
      eventID = eventID

      # Initialize payment with paystack 
      initialization_url = f'{self.base_url}/transaction/initialize'
      domain = get_current_site(kwargs.get('request')).domain

      data = {
         "email": email,
          "amount": amount,
          "Currency": "NGN",
          "callback_url": f'http://{domain}/payments/verify_payment'}


      response = requests.post(initialization_url, headers=self.headers, json=data)

      if response.status_code == 200:
          payment_data = response.json()
          payment_url = payment_data.get("data", {}).get("authorization_url")
          if payment_url:
              # print(payment_data) # for debugging
              print(payment_url) # for debugging
              data = {
                  "payment_data": payment_data,

              }
              return HttpResponse(json.dumps(data), status=200)
          else:
              return JsonResponse(
                  {"error": "Payment URL not found"}, status=400
              )
      else:
          return JsonResponse(
              {"error": "Payment initialization failed"}, status=400
          )
