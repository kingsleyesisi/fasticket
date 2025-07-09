from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from . import serializers
import os

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            if self.request.user.is_authenticated:
                return Ticket.objects.filter(user=self.request.user)
            else:
                return Ticket.objects.none()
        return Ticket.objects.all()

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        ticket = self.get_object()
        if ticket.check_in():
            return Response({'message': 'Check-in successful'})
        return Response(
            {'error': 'Check-in failed. Ticket may be invalid or already used.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        ticket = self.get_object()
        serializer = serializers.TicketTransferSerializer(data=request.data)
        
        if serializer.is_valid():
            if ticket.transfer_ticket(
                request.user,
                serializer.validated_data['new_holder_name'],
                serializer.validated_data['new_holder_email'],
                serializer.validated_data['new_holder_phone']
            ):
                return Response({'message': 'Ticket transferred successfully'})
            return Response(
                {'error': 'Transfer failed. Ticket may be invalid or not transferable.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        ticket = self.get_object()
        if ticket.request_refund():
            return Response({'message': 'Refund request submitted successfully'})
        return Response(
            {'error': 'Refund request failed. Ticket may be invalid or already used.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def verify(self, request):
        serializer = serializers.TicketVerificationSerializer(data=request.data)
        if serializer.is_valid():
            ticket = get_object_or_404(
                Ticket,
                ticket_code=serializer.validated_data['ticket_code']
            )
            return Response({
                'valid': ticket.status == 'paid' and not ticket.checked_in,
                'ticket': self.get_serializer(ticket).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = serializers.EventTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EventTicket.objects.all()
        if self.action == 'list':
            return queryset.filter(event_date__gte=timezone.now())
        return queryset

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        ticket = self.get_object()
        if ticket.reserve_ticket():
            return Response({'message': 'Ticket reserved successfully'})
        return Response(
            {'error': 'Reservation failed. Ticket may be unavailable.'},
            status=status.HTTP_400_BAD_REQUEST
        )