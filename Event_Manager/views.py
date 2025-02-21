from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer
from .models import Events



class CreateEventView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
        
    def get(self, request):
        try:
            if permission_classes:
                return Response({'M':"it i authentiated"}, status=200)
            else:
                return HttpResponse("user")
        except Exception as e:
            return Response(e)
    def post(self, request):
        return HttpResponse('This is the post request')

    def put(self, request):
        return HttpResponse('This is a put request')
        return HttpResponse('This is a put request')
    
    def delete(self, request):
        return HttpResponse('this is a delete request')


class CreateEvent(APIView):
    """
    Create a new event. Only authenticated users can create events.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_pk = user.pk
        
        data = request.data.copy()
        data['user'] = user_pk

        serializer = EventSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Event created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        print(serializer.errors)
        print(type(user_pk))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetEvent(APIView):
    """
    Get all events.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        events = Events.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

def CreateView(request):
    pass 
    return render(request, 'form.html', status=200)