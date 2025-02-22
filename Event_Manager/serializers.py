from rest_framework import serializers
from .models import Events, Tickets, TicketCategories
from rest_framework import serializers

class TicketCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategories
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    categories = TicketCategoriesSerializer(many=True, required=False)

    class Meta:
        model = Events
        fields = '__all__'

    def validate(self, data):
        if data.get('is_paid') and not data.get('categories'):
            raise serializers.ValidationError("Categories are required for paid events.")
        return data

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])  # Extract ticket categories
        event = Events.objects.create(**validated_data)

        # Create ticket categories for the event if it is paid
        if event.is_paid:
            for category_data in categories_data:
                TicketCategories.objects.create(event=event, **category_data)

        return event


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = '__all__'
