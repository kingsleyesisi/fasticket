from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
from .permissions import HasValidTokenPermission



# Login View
class CustomAuthToken(ObtainAuthToken):
  throttle_classes = [UserRateThrottle]

  def post(self, request, *args, **kwargs):
    try:
      username_or_email = request.data.get('username') or request.data.get('email')
      password = request.data.get('password')

      if '@' in username_or_email:
        user = User.objects.get(email=username_or_email)
      else:
        user = User.objects.get(username=username_or_email)

      if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

      token, created = Token.objects.get_or_create(user=user)
      return Response({
        'token': token.key,
        'user_id': user.pk,
        'username': user.username,
        'email': user.email
      })
    except User.DoesNotExist:
      return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
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


      if not username or not password or not email or not first_name or not last_name or not phone:
          return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)

      if User.objects.filter(username=username).exists():
          return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

      user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
      UserProfile.objects.create(user=user, phone=phone, company=company)
      token, created = Token.objects.get_or_create(user=user)
      return Response({
          'token': token.key,
          'user_id': user.pk,
          'username': user.username,
          'email': user.email
      }, status=status.HTTP_201_CREATED)
  
# Test bearer token
@api_view(['GET'])
@permission_classes([HasValidTokenPermission])
def test(request):
    return Response({"message": "Access granted"}, status=status.HTTP_200_OK)