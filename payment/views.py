from django.shortcuts import render, redirect, get_object_or_404
from .models import Payments
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.response import Response  
from .paystack import Paystack
import json

class InitializePaymentView(APIView):
  def post(self, request, *args, **kwargs):
          email = request.data.get('email')
          amount = request.data.get('amount')
          eventID = request.data.get('eventID')

          if not email or not amount:
              return Response({'error': 'Please provide both email and amount'}, status=status.HTTP_400_BAD_REQUEST)
          paystack = Paystack()
          response = paystack.Pay(email, amount, eventID, request=request)

          if response.status_code == 302 or 200:
              response_data = dict(json.loads(response.content.decode('utf-8')))
              print(response_data, type(response_data))
              
              return JsonResponse({'data': response_data['payment_data']['data']}, status=200)

          return JsonResponse({'error': 'Payment initialization failed'}, status=response.status_code)


def verify_payment(request, ref):
    payment = get_object_or_404(Payments, reference=ref)
    try:
        verified = payment.verify_payment()
    except Exception as e:
        print(f"Error verifying payment: {e}")
        return HttpResponse("Payment verification failed. Please try again.", status=400)

    if verified:
        print("Payment verified")
        return HttpResponse('Success')

    return render(request, 'index.html', {"error": "Payment verification failed."})
