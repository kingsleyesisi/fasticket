from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .models import UserProfile, PasswordResetOTP, RegistrationOTP
from .serializers import UserProfileSerializer, RequestOTPSerializer, VerifyOTPSerializer
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
from .permissions import HasValidTokenPermission
from django.utils.timezone import now
from django.core.mail import EmailMessage
from datetime import timedelta
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
import random

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class GetUserInfo(APIView):
    """
    API view to get user information by user ID.
    
    Permissions: AllowAny (no authentication required)
    
    Allowed HTTP Methods:
      - GET
    
    Path Parameters:
      - user_id (int): The ID of the user to retrieve information for.
    
    Response:
      - 200 OK: User information including profile data
      - 404 Not Found: If user does not exist
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'profile': {
                    'phone': user_profile.phone,
                    'company': user_profile.company,
                    'location': user_profile.location,
                    'created_at': user_profile.created_at,
                    'updated_at': user_profile.updated_at,
                }
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

# Login View

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get('username') or attrs.get('email')
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')
        else:
            attrs['username'] = username_or_email

        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [UserRateThrottle]

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


class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp: 
            print('Please provide email and OTP') # Debug
            return Response({'error': 'Please provide both email and OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            pending_registration = RegistrationOTP.objects.get(email=email, otp=otp)
        except RegistrationOTP.DoesNotExist:
            print('Invalid OTP')
            return Response({'error': 'Invalid OTP or email'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pending_registration.is_valid():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the real user
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

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)

        pending_registration.delete()

        return Response({
            "message": "Registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
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
    - first_name (str, optional): User's first name
    - last_name (str, optional): User's last name
    - email (str, optional): User's email address
    - phone (str, optional): User's phone number
    - company (str, optional): User's company
    - location (str, optional): User's location

  Response:
    - 200 OK: Updated user and profile data
    - 400 Bad Request: Validation errors
  """
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticated]
  
  def put(self, request, *args, **kwargs):
    user = request.user
    data = request.data

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(
            user=user,
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            location=data.get('location', '')
        )

    # Update User model fields
    user_updated = False
    if 'first_name' in data:
        user.first_name = data['first_name']
        user_updated = True
    if 'last_name' in data:
        user.last_name = data['last_name']
        user_updated = True
    if 'email' in data:
        # Check if email already exists for another user
        if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = data['email']
        user_updated = True
    
    if user_updated:
        user.save()

    # Update UserProfile fields
    profile_updated = False
    if 'phone' in data:
        user_profile.phone = data['phone']
        profile_updated = True
    if 'company' in data:
        user_profile.company = data['company']
        profile_updated = True
    if 'location' in data:
        user_profile.location = data['location']
        profile_updated = True
    
    if profile_updated:
        user_profile.save()

    # Return updated user data
    response_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile': {
            'phone': user_profile.phone,
            'company': user_profile.company,
            'location': user_profile.location,
            'created_at': user_profile.created_at,
            'updated_at': user_profile.updated_at,
        }
    }

    return Response({
        'message': 'Profile updated successfully',
        'data': response_data
    }, status=status.HTTP_200_OK)

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
            otp_record.delete()

            # Generate access and refresh tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Password reset successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# Test bearer token (for Debugging)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

