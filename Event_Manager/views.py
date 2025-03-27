from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer, TicketSerializer
from .models import Events, Tickets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

class CreateEvent(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk

        if 'tickets' in data and isinstance(data['tickets'], (str, list)):
            if isinstance(data['tickets'], str):
                try:
                    data['tickets'] = json.loads(data['tickets'])
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON for tickets."}, status=status.HTTP_400_BAD_REQUEST)
                
        if 'hosts' in data and isinstance(data['hosts'], (str, list)):
            if isinstance(data['hosts'], str):
                try:
                    data['hosts'] = json.loads(data['hosts'])
                    print(data['hosts'])
                except json.JSONDecodeError:    
                    return Response({'error': "Invalid Json for Host"}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print('event created successfully')
            return Response(
                {"message": "Event created successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        print("Serializer Errors:", serializer.errors)  # Debug
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
        data = {"status": "success", 
                "data": serializer.data}
        return Response(data)

class GetParticularEvent(APIView):
    """
    Get a particular Event by Event ID
    
    Args: 
        int: -> 8303 (EventID)

    returns: 
        dict: The information about a particular event
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Events, pk=pk)
        if event:
            serializer = EventSerializer(event)
            return Response({"status": "success", "data": serializer.data})
        return Response({'status': "Error", "data": "Event not found"}, status=status.HTTP_204_NO_CONTENT)
    
class UpdateEventView(APIView):
    """
    Update an existing event. Only authenticated users can update events.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        event = get_object_or_404(Events, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if request.user.pk != event.user.pk:
            return Response({"message": "You do not have permission to update this event"})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Event updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteEvent(APIView):
    """
    Delete an existing event. Only authenticated users can delete events.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        event = get_object_or_404(Events, pk=pk)
        if request.user.pk != event.user.pk:
            return Response({"error": "You do not have permission to delete this event"}, status=status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)

def CreateView(request):
    return render(request, 'form.html', status=200)