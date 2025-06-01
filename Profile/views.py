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
from django.core.mail import EmailMessage
from datetime import timedelta
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password

# Login View
class CustomAuthToken(ObtainAuthToken):
  """
  Custom authentication token view that extends Django REST Framework's ObtainAuthToken.
  It allows users to log in using either their username or email.

  Throttle Classes: UserRateThrottle (limits request frequency per user)

  Allowed HTTP Methods:
    - POST

  Request Body (POST):
    - username (str, optional): User's username or email. If 'email' is also provided, 'username' takes precedence if it's not an email format.
    - email (str, optional): User's email (used if 'username' is not provided or is not an email).
    - password (str): User's password.

  Response:
    - 200 OK: {'token': token.key, 'user_id': user.pk, 'username': user.username, 'email': user.email}
    - 400 Bad Request: {'error': 'Incorrect password'} or {'error': 'User Does Not Exist'}
    - 500 Internal Server Error: {'error': str(e)} (for other exceptions)
  """
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
        
        # This check and delete any token older than 6 hours
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
    """
    API view to initiate user registration by sending an OTP to the user's email.

    Permissions: AllowAny

    Allowed HTTP Methods:
      - POST

    Request Body (POST):
      - username (str): Desired username.
      - password (str): Desired password.
      - email (str): User's email address.
      - first_name (str): User's first name.
      - last_name (str): User's last name.
      - phone (str): User's phone number.
      - company (str, optional): User's company.
      - location (str, optional): User's location.

    Response:
      - 200 OK: {"message": "OTP sent to your email. Please verify to complete registration."}
      - 400 Bad Request: {'error': 'Please provide all required fields'} or {'error': 'Username already exists'} or {'error': 'Email already exists'}
    """
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
            print('all field required') # for deugging 
            return Response(
                {'error': 'Please provide all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            print('Username already Exist') # for debuging
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            print('email Aready exist') # for debugging
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{random.randint(100000, 999999)}"
        hashed_password = make_password(password)

        RegistrationOTP.objects.create(
            username=username,
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company or "",
            location=location or "",
            otp=otp
        )
        
        subject = "Registration Confirmation"
        context = {'otp': otp}
        body = render_to_string('emails/registration_mail.html', context)
        mail = EmailMessage(subject, body, from_email='no-reply@fasticket.com', reply_to=['support@fasticket.com'], to=[email])
        mail.content_subtype = 'html'
        mail.send()
        
        return Response(
            {"message": "OTP sent to your email. Please verify to complete registration."},
            status=status.HTTP_200_OK
        )

class RegisterUser(APIView):
  """
  API view to complete user registration by verifying the OTP.

  Permissions: AllowAny

  Allowed HTTP Methods:
    - POST

  Request Body (POST):
    - email (str): User's email address.
    - otp (str): The OTP received by the user.

  Response:
    - 201 Created: {"message": "Registration successful", "token": token.key, "user_id": user.pk, "username": user.username, "email": user.email}
    - 400 Bad Request: {'error': 'Please provide both email and OTP'} or {'error': 'Invalid OTP or email'} or {'error': 'OTP has expired'}
  """
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
      email = request.data.get('email')
      otp = request.data.get('otp')

      if not email or not otp: 
         print('Please provid email and OTP') # Debug
         return Response({'error': 'Please provide both email and OTP'}, status=status.HTTP_400_BAD_REQUEST)
      
      try:
         pending_registration = RegistrationOTP.objects.get(email=email, otp=otp)
  
      except RegistrationOTP.DoesNotExist:
        print('Invalid OTP')
        return Response({'error': 'Invalid OTP or email'}, status=status.HTTP_400_BAD_REQUEST)
      
      if not pending_registration.is_valid():
        return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
      
      # Create the real user
      # Use the pre-hashed password from pending_registration
      user = User(
          username=pending_registration.username,
          email=pending_registration.email,
          first_name=pending_registration.first_name,
          last_name=pending_registration.last_name
      )
      user.password = pending_registration.password  # Assign already hashed password
      user.save()

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
  """
  API view to update the authenticated user's profile.

  Permissions: IsAuthenticated (implicitly, as it uses request.user)

  Allowed HTTP Methods:
    - PUT

  Request Body (PUT):
    - Fields from UserProfileSerializer (e.g., company, phone, location). All fields are optional for partial updates.

  Response:
    - 200 OK: UserProfileSerializer.data (updated profile data)
    - 400 Bad Request: serializer.errors
  """
  def put(self, request, *args, **kwargs):
    user = request.user
    data = request.data

    user_profile = UserProfile.objects.get(user=user)
    serializer = UserProfileSerializer(user_profile, data=data, partial=True)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    """
    API view to initiate the password reset process by sending an OTP to the user's email.

    Permissions: AllowAny (implicitly, not specified but typical for this action)

    Allowed HTTP Methods:
      - POST

    Request Body (POST):
      - email (str): The email address of the user requesting password reset. (Handled by RequestOTPSerializer)

    Response:
      - 200 OK: {"message": "OTP sent successfully"}
      - 400 Bad Request: serializer.errors or {"error": "User with this email does not exist"}
    """
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if not user:
                print('User with email does not exists') # for debuggig
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            otp = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.create(user=user, otp=otp)

            subject = "Password Reset Confirmation"
            context = {'otp': otp}
            body = render_to_string('emails/reset_password.html', context)
            mail = EmailMessage(subject, body, from_email='no-reply@fasticket.com', reply_to=['support@fasticket.com'], to=[email])
            mail.content_subtype = 'html'
            mail.send()

            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
  """
  API view to verify the OTP and reset the user's password.

  Permissions: AllowAny (implicitly, not specified but typical for this action)

  Allowed HTTP Methods:
    - POST

  Request Body (POST):
    - email (str): User's email address.
    - otp (str): The OTP received by the user.
    - new_password (str): The new password for the user.
    (Handled by VerifyOTPSerializer)

  Response:
    - 200 OK: {"message": "Password reset successful", "token": new_token.key}
    - 400 Bad Request: serializer.errors or {"error": "Invalid email"} or {"error": "Invalid or expired OTP"}
  """
  def post(self, request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
      email = serializer.validated_data['email']
      otp = serializer.validated_data['otp']
      new_password = serializer.validated_data['new_password']

      user = User.objects.filter(email=email).first()
      if not user:
        print('Invalid Email')
        return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

      otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).first()
      if not otp_record or not otp_record.is_valid():
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

      # Reset password
      user.set_password(new_password)
      user.save()
      otp_record.delete()  # Remove OTP after use

      Token.objects.filter(user=user).delete()
      new_token, created = Token.objects.get_or_create(user=user)

      return Response({
        "message": "Password reset successful",
        "token": new_token.key
      }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Test bearer token (for Debugging)
@api_view(['GET'])
@permission_classes([HasValidTokenPermission])
def test(request):
    """
    A simple test endpoint to check if a bearer token is valid.

    Permissions: HasValidTokenPermission (custom permission to check token validity)

    Allowed HTTP Methods:
      - GET

    Response:
      - 200 OK: {"message": "Access granted"}
      - 401 Unauthorized (or other appropriate status from HasValidTokenPermission): If access is denied.
    """
    return Response({"message": "Access granted"}, status=status.HTTP_200_OK)