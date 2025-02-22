from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import EventSerializer, TicketCategoriesSerializer, TicketSerializer
from .models import Events, TicketCategories, Tickets

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

class TicketViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    queryset = Tickets.objects.all()
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        category_id = request.data.get("category")
        quantity = int(request.data.get("quantity", 1))

        try:
            category = TicketCategories.objects.get(id=category_id)
            if category.available_tickets < quantity:
                return Response({"error": "Not enough tickets available"}, status=status.HTTP_400_BAD_REQUEST)

            category.available_tickets -= quantity
            category.save()

            ticket = Tickets.objects.create(
                event=category.event,
                category=category,
                quantity=quantity
            )
            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
        except TicketCategories.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)



class TicketCategoriesView(APIView):
    
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
            
        queryset = TicketCategories.objects.all()
        serializer = TicketCategoriesSerializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def post(self, request):
        serializer = TicketCategoriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def CreateView(request):
    return render(request, 'form.html', status=200)