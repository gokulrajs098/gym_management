from rest_framework import serializers
from .models import Customer
from user_auth.serializers import AdminRegistrationSerializer

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = "__all__"