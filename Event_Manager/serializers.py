from rest_framework import serializers
from .models import Events, Tickets #, TicketCategories
from rest_framework import serializers

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ('ticket_type', 'price', 'quantity')
        # fields = '__all__'
class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, required=False)

    class Meta:
        model = Events
        fields = '__all__'

    def validate(self, attrs):
        is_paid = attrs.get('is_paid', False)
        tickets = self.initial_data.get('tickets')
        if is_paid and (tickets is False or len(tickets) == 0):
            raise serializers.ValidationError("Paid events must include at least one ticket.")

        return attrs


    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])  # Extract ticket
        event = Events.objects.create(**validated_data)

        # Create ticket  for the event if it is paid
        if event.is_paid:
            for ticket in tickets_data:
                Tickets.objects.create(event=event, **ticket)

        return event