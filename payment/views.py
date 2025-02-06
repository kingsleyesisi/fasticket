from django.shortcuts import render, redirect, get_object_or_404
from .models import Payments
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
                    else:
                            paystack = Paystack()
                            response = paystack.Pay(email, amount, eventID, request=request)

                    if response.status_code == 302 or 200:
                            response_data = dict(json.loads(response.content.decode('utf-8')))
                            data = response_data['payment_data']['data']
                            reference = data['reference']
                            store_reference = Payments.objects.create(reference=reference, amount=amount, email=email)
                            print(f'This is the reference {store_reference}')
                            return JsonResponse(data, status=200)

                    return JsonResponse({'error': 'Payment initialization failed'}, status=response.status_code)

class CallBack(APIView):
  def get(self, request):
    trxref = request.GET.get('trxref')
    if not trxref:
      return HttpResponse("Transaction reference not provided.", status=400)
    
    payment = get_object_or_404(Payments, reference=trxref)
    paystack = Paystack()
    status = paystack.verify(trxref)

    if status == True:
        payment.Verified = True
        payment.save()
        return JsonResponse({"data": "success"}, status=200)

    else:
      reason = status
      return JsonResponse(reason, status=400)  

class ListPaymentsView(APIView):
    def get(self, request, *args, **kwargs):
        payments = Payments.objects.all()
        payments_list = [
            {
                'reference': payment.reference,
                'amount': payment.amount,
                'email': payment.email,
                'verified': payment.Verified,
            }
            for payment in payments
        ]
        return JsonResponse(payments_list, safe=False, status=200)