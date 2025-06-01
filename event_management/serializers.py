from rest_framework import serializers
from .models import Event, Tickets, Hosts #, TicketCategories
from rest_framework import serializers

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ('ticket_type', 'price', 'quantity')
        # fields = '__all__'

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hosts
        fields = ('role', 'name', 'email', 'social_media')

class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)
    hosts = HostSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, attrs):
        """
        Validate the data.

        This method checks if the event is marked as paid and ensures that at least one ticket is included.
        If the event is paid and no tickets are provided, a ValidationError is raised.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes, including the tickets.

        Raises:
            serializers.ValidationError: If the event is paid and no tickets are provided.
        """

        is_paid = attrs.get('is_paid', False)
        tickets = self.initial_data.get('tickets')
        if is_paid and (tickets is None or len(tickets) == 0):
            raise serializers.ValidationError("Paid events must include at least one ticket.")

        attrs['tickets'] = tickets
        attrs['hosts'] = self.initial_data.get('hosts')
        return attrs

    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])  # Extract ticket
        host_data = validated_data.pop('hosts', [])  # Extract host if present
        event = Event.objects.create(**validated_data)

        # Create ticket  for the event if it is paid
        if event.is_paid:
            for ticket in tickets_data:
                Tickets.objects.create(event=event, **ticket)
        
        # Assign host to the event if provided
        if host_data:
            for host in host_data:
                Hosts.objects.create(event=event, **host)
                
        return event