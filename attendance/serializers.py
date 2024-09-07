from rest_framework import serializers
from .models import GymAttendance
from gym_details.serializers import GymDetailsSerializer  # Adjust import path
from user_auth.serializers import UserRegistrationSerializer  # Adjust import path

class GymAttendanceSerializer(serializers.ModelSerializer):
    gym = GymDetailsSerializer()  # Use the imported serializer
    user = UserRegistrationSerializer()  # Use the imported serializer
    class Meta:
        model = GymAttendance
        fields = ['user', 'gym', 'check_in_time', 'check_out_time', 'checked_in']
