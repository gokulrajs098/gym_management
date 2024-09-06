from rest_framework import serializers
from .models import Event
from gym_details.serializers import GymDetailsSerializer
from gym_details.models import GymDetails

class EventSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'date', 'timing', 'location', 'description', 'guest_name', 'gym']