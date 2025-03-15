from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import UserProfile, PasswordResetOTP
from .serializers import UserProfileSerializer, RequestOTPSerializer, VerifyOTPSerializer
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
from .permissions import HasValidTokenPermission
from django.utils.timezone import now
import random
from django.core.mail import send_mail

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

class RegisterUser(APIView):
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
      username = request.data.get('username')
      password = request.data.get('password')
      email = request.data.get('email')
      first_name = request.data.get('first_name')
      last_name = request.data.get('last_name')
      phone = request.data.get('phone')
      company = request.data.get('company')
      location = request.data.get('location')


      if not username or not password or not email or not first_name or not last_name or not phone:
          print('Error: fields required')  # Log to Terminal for debugging
          return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)

      if User.objects.filter(username=username).exists():
          print("Error: user already exist")  # Log to Terminal for debugging
          return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
      if User.objects.filter(email=email).exists():
         print('Error: email already exist')  # Log to Terminal for debugging
         return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

      user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
      UserProfile.objects.create(user=user, phone=phone, company=company, location=location)
      token, created = Token.objects.get_or_create(user=user)
      print(f'Registration successful:   {user.username}') # Log to Terminal for debugging
      return Response({
          'token': token.key,
          'user_id': user.pk,
          'username': user.username,
          'email': user.email
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
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is {otp}. It expires in 5 minutes.",
                "no-reply@example.com",
                [user.email],
                fail_silently=False,
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

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Test bearer token
@api_view(['GET'])
@permission_classes([HasValidTokenPermission])
def test(request):
    return Response({"message": "Access granted"}, status=status.HTTP_200_OK)