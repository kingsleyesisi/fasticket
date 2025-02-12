from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token

class HasValidTokenPermission(BasePermission):
    """
    Custom permission to allow access only if the user has a valid token.
    """

    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                token_key = token.split(' ')[1]
                token_obj = Token.objects.get(key=token_key)
                user = token_obj.user
                return user.is_authenticated
            except (IndexError, Token.DoesNotExist):
                return False
        return False
