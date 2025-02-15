from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer, TicketSerializer
from .models import Events, Tickets



class CreateEventView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
        
    def get(request, *args, **kwagr):
        try:
            if permission_classes:
                return Response({'M':"it i authentiated"}, status=200)
            else:
                return HttpResponse("user")
        except Exception as e:
            return Response(e)
    def post(request, *arg, **kwagr):
        yield HttpResponse('This is the post request')

    def put(request, *args, **kwargs):
        pass
        return HttpResponse('This is a put request')
    
    def delete(request, *args, **kwargs):
        return HttpResponse('this is a delete request')


class CreateEvent(APIView):
    """
    Create a new event. Only authenticated users can create events.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Event created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class GetEvent(APIView):
    """
    Get all events.
    """
    def get(self, request, format=None):
        events = Events.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
