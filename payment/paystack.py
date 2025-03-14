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
      """
      Initialize the payment
      Args:
        Email, A
      """
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
          "callback_url": f'http://{domain}/payments/verify_payment' # Change during production 
          }


      response = requests.post(initialization_url, headers=self.headers, json=data)
    #   print(response.text)
      message = response.json().get('message')

    #   print(message)
      if response.status_code == 200:
          payment_data = response.json()
          payment_url = payment_data.get("data", {}).get("authorization_url")
          if payment_url:
              data = {
                  "payment_data": payment_data,

              }
              return HttpResponse(json.dumps(data), status=200)
          else:
              return JsonResponse(
                  {"error": "Payment URL not found"}, status=400
              )
      else:
        message = response.json().get('message')
        return JsonResponse(
              {"error": message}, status=400
          )
    

    # Verification of the Payment 
    def verify(self, reference):
      """
      Verify payment with Paystack using the provided reference

      Args: 
        reference (eg<38s3039>)

      Returns:
        
      """
      verify_url = f"{self.base_url}/transaction/verify/{reference}"
      
      try:
          response = requests.get(verify_url, headers=self.headers)
          response.raise_for_status()

          verification_data = response.json()

          if verification_data['data']['status'] == 'success':
              return True
          
          else: 
              r = verification_data['data']['status']
              reason = verification_data['data']['gateway_response']
              return {'data': reason}
          
      except requests.RequestException as e:
        print(f"Error verifying payment: {e}")
        return None
      
if __name__ == "__main__":
    amount = 2000
    email = 'testemail@gmail.com'
    eventID = 'event123'
    paystack = Paystack()
    request = None  # Replace with actual request object if available
    initiate = paystack.Pay(email=email, amount=amount, eventID=eventID, request=request)
    print(initiate.content)