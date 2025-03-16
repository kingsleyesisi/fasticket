from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import UserProfile, PasswordResetOTP, RegistrationOTP
from .serializers import UserProfileSerializer, RequestOTPSerializer, VerifyOTPSerializer
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
from .permissions import HasValidTokenPermission
from django.utils.timezone import now
import random
from django.core.mail import send_mail
from datetime import timedelta

# Login View
class CustomAuthToken(ObtainAuthToken):
  throttle_classes = [UserRateThrottle]

  def post(self, request, *args, **kwargs):
    try:
      username_or_email = request.data.get('username') or request.data.get('email').lower()
      password = request.data.get('password')
      
      user = User.objects.filter(email=username_or_email).first() if '@' in username_or_email else User.objects.filter(username=username_or_email).first()
      if user:
        if not user.check_password(password):
          print("Incorrect Password")
          return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        
        # This check and delete any token older than 2 hours 
        if token.created < now() - timedelta(hours=6):
           token.delete()
           token = Token.objects.create(user=user)
           print(token)

        user.last_login = now()
        user.save(update_fields=["last_login"])
        print(f'logged in successful {user.username}')  # Log to Terminal for debugging
        return Response({
          'token': token.key,
          'user_id': user.pk,
          'username': user.username,
          'email': user.email,
        })
      else:
        print("User Does Not Exist") # Log to Terminal for debugging
        return Response({'error': 'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
      return Response({'error': 'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      print(e)  # Log to Terminal for debugging
      return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Registration OTP
class InitiateRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone = request.data.get('phone')
        company = request.data.get('company')
        location = request.data.get('location')

        if not all([username, password, email, first_name, last_name, phone]):
            return Response(
                {'error': 'Please provide all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{random.randint(100000, 999999)}"

        RegistrationOTP.objects.create(
            username=username,
            password=password,  # Plaintext for demo
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company or "",
            location=location or "",
            otp=otp
        )

        # Send OTP via email (Note that a well structured email with proper styling should be created)
        body = f"""
                  <html>
                    <head>
                      <style>
                        body{{
                          font-family: Arial, sans-serif;
                        }}
                        h2 {{
                          color: #007bff;   
                        }}
                        b{{
                          background-color: #1b1a1a;
                          color: #ffffff;
                          padding: 10px 20px;
                          border: none;
                          border-radius: 5px;
                        }}
                        em{{
                          color: red;
                          margin-top: 100px;
                        }}
                        
                      </style>
                    </head>

                    <body>
                      <h2>Registration OTP</h2>
                      <p> Your Comfirmation OTP is <b> {otp}.</b> It expires in 30 minutes.</p>
                    
                    <p><em>If you did not request this OTP, please ignore this email. </em></p>
                    </body>
                  </html>
                    """
        send_mail(
            subject="Your Registration OTP",
            message=body,
            from_email='noreplay@domain.com',
            recipient_list=[email],
            fail_silently=False,
            html_message=body
        )

        return Response(
            {"message": "OTP sent to your email. Please verify to complete registration."},
            status=status.HTTP_200_OK
        )

class RegisterUser(APIView):
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
      email = request.data.get('email')
      otp = request.data.get('otp')

      if not email or not otp: 
         return Response({'error': 'Please provide both email and OTP'}, status=status.HTTP_400_BAD_REQUEST)
      
      # Retrive the pending registration 

      try:
         pending_registration = RegistrationOTP.objects.get(email=email, otp=otp)
  
      except RegistrationOTP.DoesNotExist:
        return Response({'error': 'Invalid OTP or email'}, status=status.HTTP_400_BAD_REQUEST)
      
      # Check if the OTP is still valid 
      if not pending_registration.is_valid():
        return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
      
      # Create the real user 
      user = User.objects.create_user(
          username=pending_registration.username,
          password=pending_registration.password,
          email=pending_registration.email,
          first_name=pending_registration.first_name,
          last_name=pending_registration.last_name
      )

      UserProfile.objects.create(
          user=user,
          phone=pending_registration.phone,
          company=pending_registration.company,
          location=pending_registration.location
      )

      # Generate a new token for the user
      token, created = Token.objects.get_or_create(user=user)

      pending_registration.delete()

      return Response({
         "message": "Registration successful",
         "token": token.key,
         "user_id": user.pk,
          "username": user.username,
          "email": user.email
      }, status=status.HTTP_201_CREATED)

class UpdateProfile(APIView):
  def put(self, request, *args, **kwargs):
    user = request.user
    data = request.data

    user_profile = UserProfile.objects.get(user=user)
    serializer = UserProfileSerializer(user_profile, data=data, partial=True)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if not user:
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            otp = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.create(user=user, otp=otp)

            # Send OTP via email
            subject = "Fasticket - Reset Password OTP"
            body = f"""
                  <html>
                    <head>
                      <style>
                        body{{
                          font-family: Arial, sans-serif;
                        }}
                        h2 {{
                          color: #007bff;   
                        }}
                        b{{
                          background-color: #1b1a1a;
                          color: #ffffff;
                          padding: 10px 20px;
                          border: none;
                          border-radius: 5px;
                        }}
                        em{{
                          color: red;
                          margin-top: 100px;
                        }}
                        
                      </style>
                    </head>

                    <body>
                      <h2>Password Reset OTP</h2>
                      <p> Your OTP for password reset is <b> {otp}.</b> It expires in 30 minutes.</p>
                    
                    <p><em>If you did not request this OTP, please ignore this email. </em></p>
                    </body>
                  </html>
                    """
            send_mail(
                subject=subject,
                message=body,
                from_email="no-reply@example.com", # Change during production
                recipient_list=[user.email],
                fail_silently=False,
                html_message=body
            )

            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
  def post(self, request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
      email = serializer.validated_data['email']
      otp = serializer.validated_data['otp']
      new_password = serializer.validated_data['new_password']

      user = User.objects.filter(email=email).first()
      if not user:
        return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

      otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).first()
      if not otp_record or not otp_record.is_valid():
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

      # Reset password
      user.set_password(new_password)
      user.save()
      otp_record.delete()  # Remove OTP after use

      # Change the token after the password has been changed
      Token.objects.filter(user=user).delete()
      new_token, created = Token.objects.get_or_create(user=user)

      return Response({
        "message": "Password reset successful",
        "token": new_token.key
      }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Test bearer token
@api_view(['GET'])
@permission_classes([HasValidTokenPermission])
def test(request):
    return Response({"message": "Access granted"}, status=status.HTTP_200_OK)