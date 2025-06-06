from django.shortcuts import render, redirect, get_object_or_404
from .models import Payments
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status 
from rest_framework.response import Response  
from .paystack import Paystack
import json
from event_management.models import Tickets as EventTicketType
from django.contrib.auth import get_user_model
from ticket_management.models import Ticket as PurchasedTicket
from django.db import transaction, IntegrityError
from django.db.models import F
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings # To get DEFAULT_FROM_EMAIL

User = get_user_model()

class InitializePaymentView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
            name = request.data.get('name')
            email = request.data.get('email')
            # amount_from_request = request.data.get('amount') # We'll use amount from the ticket type
            ticket_type_id = request.data.get('ticket_type_id') # Changed from eventID for clarity

            if not email: # Amount check will be based on ticket_type_id
                return Response({'error': 'Please provide an email.'}, status=status.HTTP_400_BAD_REQUEST)

            if not ticket_type_id:
                return Response({'error': 'Please provide ticket_type_id.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                ticket_type = EventTicketType.objects.get(id=ticket_type_id)
            except EventTicketType.DoesNotExist:
                return Response({'error': 'Invalid ticket_type_id.'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError: # Handles if ticket_type_id is not a valid format (e.g. not int/uuid)
                 return Response({'error': 'Invalid ticket_type_id format.'}, status=status.HTTP_400_BAD_REQUEST)


            amount = float(ticket_type.price) # Get amount from the ticket type model

            if ticket_type.available <= 0:
                return Response({'error': 'This ticket type is sold out.'}, status=status.HTTP_400_BAD_REQUEST)

            paystack = Paystack()
            # Pass ticket_type.id (which is ticket_type_id) as the eventID argument to Paystack and Payments model
            # The Paystack().Pay method doesn't actually use eventID for its API call, 
            # but we store it in our Payments model.
            response = paystack.Pay(email, amount, ticket_type_id, request=request)

            if response.status_code == 200:
                try:
                    response_data = dict(json.loads(response.content.decode('utf-8')))
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Failed to decode Paystack response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                payment_api_data = response_data.get('payment_data', {}).get('data', {})
                if not payment_api_data:
                    # Handle case where payment_data or data is missing - though Paystack.Pay should return 400 earlier
                    return JsonResponse({'error': 'Invalid response structure from Paystack'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                reference = payment_api_data.get('reference')
                if not reference:
                    return JsonResponse({'error': 'Reference not found in Paystack response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Storing ticket_type_id in the 'eventID' field of the Payments model
                Payments.objects.create(reference=reference, amount=amount, email=email, name=name, eventID=ticket_type_id)
                return JsonResponse(payment_api_data, status=200)
            
            # If response.status_code is not 200, try to parse error message
            try:
                message = dict(json.loads(response.content.decode('utf-8')))
                error_message = message.get('error', 'Unknown error from Paystack')
            except json.JSONDecodeError:
                error_message = 'Failed to decode error response from Paystack'
            except AttributeError: # If response.content is not bytes
                error_message = 'Invalid error response format from Paystack'

            return JsonResponse({'error': error_message}, status=response.status_code if response.status_code >= 400 else status.HTTP_400_BAD_REQUEST)

class CallBack(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        trxref = request.GET.get('trxref')
        if not trxref:
            # Consider returning a more user-friendly page or JSON response
            return HttpResponse("Transaction reference not provided.", status=400)

        try:
            payment = Payments.objects.get(reference=trxref)
        except Payments.DoesNotExist:
            # Consider returning a more user-friendly page or JSON response
            return HttpResponse("Payment record not found for this reference.", status=404)

        # If payment already verified by a previous callback, prevent reprocessing
        if payment.Verified:
            # Potentially redirect to a success page or return a specific JSON response
            # For now, just acknowledge it's already verified.
            # Also, ensure the client-side knows how to handle this (e.g. redirect to ticket, orders page)
            return JsonResponse({"data": "success", "message": "Payment already verified."}, status=200)

        paystack = Paystack()
        verification_status = paystack.verify(trxref) # verification_status can be True or a dict on error

        if verification_status is True:
            try:
                with transaction.atomic():
                    # Refresh payment from DB to ensure we have the latest version inside the transaction
                    payment_to_update = Payments.objects.select_for_update().get(pk=payment.pk)
                    
                    if payment_to_update.Verified: # Double check after locking
                         return JsonResponse({"data": "success", "message": "Payment already verified (checked in transaction)."}, status=200)

                    # 1. Retrieve User
                    user = None # Initialize user to None
                    try:
                        user = User.objects.get(email=payment_to_update.email)
                    except User.DoesNotExist:
                        print(f"No registered user found for email {payment_to_update.email}. Proceeding with guest checkout.")

                    # 2. Retrieve Ticket Type
                    try:
                        ticket_type = EventTicketType.objects.select_for_update().get(id=payment_to_update.eventID) # eventID now stores ticket_type_id
                    except EventTicketType.DoesNotExist:
                        print(f"EventTicketType with id {payment_to_update.eventID} not found for payment {payment_to_update.reference}.")
                        # Similar to user not found, payment is good, but context for ticket is missing.
                        return JsonResponse({'error': f'Ticket type {payment_to_update.eventID} not found. Payment verification successful but ticket not created.'}, status=400)


                    # 3. Check Availability & Decrement Quantity (Atomic)
                    if ticket_type.available <= 0:
                        print(f"Ticket type {ticket_type.id} is sold out. Payment {payment_to_update.reference} was processed but no ticket issued.")
                        # This is an oversell scenario. Payment is verified, but no ticket can be issued.
                        # Mark payment as verified but flag for review/refund.
                        payment_to_update.Verified = True 
                        payment_to_update.save()
                        return JsonResponse({'error': 'Tickets are sold out. Your payment was successful but no ticket could be issued. Please contact support.', "data": "oversold"}, status=200) # 200 because payment is fine, but needs follow up

                    ticket_type.available = F('available') - 1
                    ticket_type.save(update_fields=['available'])
                    ticket_type.refresh_from_db() # Get the new available

                    # 4. Create PurchasedTicket
                    purchased_ticket = PurchasedTicket.objects.create(
                        user=user,
                        ticket_type=ticket_type, # Link to the EventTicketType model
                        category='event', # Assuming 'event' is a valid choice
                        price=payment_to_update.amount, # Use amount from verified payment
                        status='paid',
                        holder_name=payment_to_update.name if payment_to_update.name else user.get_full_name(), # Fallback for holder name
                        holder_email=payment_to_update.email,
                        # ticket_code and qr_code are generated by model's save()
                    )
                    
                    # Mark payment as verified ONLY after all operations succeed
                    payment_to_update.Verified = True
                    payment_to_update.save(update_fields=['Verified', 'paid_at']) # Assuming paid_at is updated in model save

                    try:
                        # Prepare email context
                        email_context = {
                            'ticket_details': {
                                'event_name': ticket_type.event.title,
                                'ticket_type': ticket_type.ticket_type,
                                'price': purchased_ticket.price,
                                'ticket_code': purchased_ticket.ticket_code,
                                'holder_name': purchased_ticket.holder_name,
                                'holder_email': purchased_ticket.holder_email,
                                # Add any other details you want in the email
                            },
                            'event_banner_url': ticket_type.event.banner.url if ticket_type.event.banner else None,
                            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
                        }
                        
                        subject = f"Your Ticket Confirmation for {ticket_type.event.title}"
                        
                        # Render HTML content
                        html_message = render_to_string('emails/ticket_confirmation_email.html', email_context)
                        
                        # Plain text message (optional, but good practice)
                        plain_message = (
                            f"Hello {purchased_ticket.holder_name},\n\n"
                            f"Thank you for your purchase! Here are your ticket details:\n"
                            f"Event: {ticket_type.event.title}\n"
                            f"Ticket Type: {ticket_type.ticket_type}\n"
                            f"Price: {purchased_ticket.price}\n"
                            f"Ticket Code: {purchased_ticket.ticket_code}\n\n"
                            f"You can view your ticket details and QR code (if applicable) by logging into your account or using the ticket code.\n\n"
                            f"Thank you,\nThe Event Team"
                        )
                        
                        send_mail(
                            subject,
                            plain_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [purchased_ticket.holder_email],
                            html_message=html_message,
                            fail_silently=False # Set to True in production if you don't want email errors to break the flow
                        )
                        print(f"Ticket confirmation email sent to {purchased_ticket.holder_email}")
                    except Exception as e:
                        # Log email sending failure
                        print(f"Failed to send ticket confirmation email to {purchased_ticket.holder_email}: {e}")
                        # Do not let email failure break the entire transaction,
                        # but it should be logged for investigation.

                    # The client might be redirected by Paystack here. 
                    # This JSON response is for API clients or if Paystack callback is handled server-side then redirected.
                    return JsonResponse({
                        "data": "success", 
                        "message": "Payment verified and ticket created successfully.",
                        "ticket_id": purchased_ticket.id,
                        "ticket_code": purchased_ticket.ticket_code
                    }, status=200)

            except IntegrityError as e: # Handles potential issues with F expression or other DB constraints
                print(f"Database integrity error during payment callback for {trxref}: {e}")
                return JsonResponse({'error': 'A database error occurred. Please contact support.'}, status=500)
            except Exception as e: # Catch any other unexpected errors
                print(f"Unexpected error during payment callback for {trxref}: {e}")
                # Do not mark payment as verified if ticket creation failed unexpectedly
                return JsonResponse({'error': 'An unexpected error occurred while creating your ticket. Please contact support.'}, status=500)
        else:
            # verification_status contains error dict from paystack.verify()
            reason = verification_status.get('data', 'Payment verification failed.') if isinstance(verification_status, dict) else 'Payment verification failed.'
            return JsonResponse({'error': reason}, status=400)


# Just for debugging
class ListPaymentsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
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