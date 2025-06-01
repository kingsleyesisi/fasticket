from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer, TicketSerializer
from .models import Event, Tickets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

class CreateEvent(APIView):
    """
    API view to create a new event.

    Authentication: TokenAuthentication
    Permissions: IsAuthenticated
    Parser Classes: MultiPartParser, FormParser, JSONParser

    Allowed HTTP Methods:
        - POST

    Request Body (POST):
        - user (int): Automatically set to the authenticated user's PK.
        - title (str): Title of the event.
        - description (str): Description of the event.
        - banner (file, optional): Banner image for the event.
        - timezone (str, optional): Timezone for the event (default: "UTC").
        - start_date (date): Start date of the event.
        - start_time (time): Start time of the event.
        - end_date (date, optional): End date of the event.
        - end_time (time, optional): End time of the event.
        - location (str, optional): Location of the event.
        - event_type (str, optional): Type of event (default: "In-person").
        - external_link (url, optional): External link for virtual events.
        - capacity (int): Capacity of the event.
        - is_paid (bool, optional): Whether the event is paid (default: False).
        - tickets (list of dict, optional): List of ticket details if the event is paid.
            Each dict should contain:
                - ticket_type (str): Type of ticket.
                - quantity (int): Number of tickets.
                - price (decimal): Price of the ticket.
        - hosts (list of dict, optional): List of host details.
            Each dict should contain:
                - name (str): Name of the host.
                - email (str, optional): Email of the host.
                - role (str): Role of the host.
                - social_media (url, optional): Social media link of the host.
                - phone (str, optional): Phone number of the host.

    Response (POST):
        - 200 OK: {"message": "Event created successfully!", "data": EventSerializer.data}
        - 400 Bad Request: {"error": "Invalid JSON for tickets."} or {"error": "Invalid Json for Host"} or serializer.errors
    """
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
    API view to retrieve all events.

    Authentication: None
    Permissions: AllowAny

    Allowed HTTP Methods:
        - GET

    Response (GET):
        - 200 OK: {"status": "success", "data": [EventSerializer.data]}
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        data = {"status": "success",
                "data": serializer.data}
        return Response(data)

class GetParticularEvent(APIView):
    """
    API view to retrieve a particular event by its ID.

    Authentication: None
    Permissions: AllowAny

    Allowed HTTP Methods:
        - GET

    Path Parameters:
        - pk (str): The ID of the event to retrieve.

    Response (GET):
        - 200 OK: {"status": "success", "data": EventSerializer.data}
        - 204 No Content: {'status': "Error", "data": "Event not found"} (If event does not exist)
        - 404 Not Found: If event does not exist (from get_object_or_404).
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event: # This check is somewhat redundant due to get_object_or_404
            serializer = EventSerializer(event)
            return Response({"status": "success", "data": serializer.data})
        # This part might not be reached if get_object_or_404 raises an exception first.
        return Response({'status': "Error", "data": "Event not found"}, status=status.HTTP_204_NO_CONTENT)

class UpdateEventView(APIView):
    """
    API view to update an existing event.

    Authentication: TokenAuthentication
    Permissions: IsAuthenticated (Only the event creator can update)

    Allowed HTTP Methods:
        - PUT

    Path Parameters:
        - pk (str): The ID of the event to update.

    Request Body (PUT):
        - Same fields as CreateEvent (POST), but all are optional (partial update).

    Response (PUT):
        - 200 OK: {"message": "Event updated successfully!", "data": EventSerializer.data}
        - 400 Bad Request: serializer.errors
        - 403 Forbidden: {"message": "You do not have permission to update this event"}
        - 404 Not Found: If event does not exist.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if request.user.pk != event.user.pk:
            return Response({"message": "You do not have permission to update this event"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Event updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteEvent(APIView):
    """
    API view to delete an existing event.

    Authentication: TokenAuthentication
    Permissions: IsAuthenticated (Only the event creator can delete)

    Allowed HTTP Methods:
        - DELETE

    Path Parameters:
        - pk (str): The ID of the event to delete.

    Response (DELETE):
        - 200 OK: {"message": "Event deleted successfully"}
        - 403 Forbidden: {"error": "You do not have permission to delete this event"}
        - 404 Not Found: If event does not exist.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user.pk != event.user.pk:
            return Response({"error": "You do not have permission to delete this event"}, status=status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)

def CreateView(request):
    """
    Renders a simple HTML form for creating an event.
    Likely used for testing or simple admin interactions directly via browser.

    Allowed HTTP Methods:
        - GET

    Response (GET):
        - Renders 'form.html' template.
    """
    return render(request, 'form.html', status=200)