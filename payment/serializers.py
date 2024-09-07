from rest_framework import serializers
from .models import Payment, Orders
from user_auth.serializers import UserRegistrationSerializer
from gym_details.serializers import GymDetailsSerializer
from gym_products.serializers import ProductSerializer

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'stripe_payment_id',
            'amount',
            'status',
            'created_at',
            'user',
            'gym',
            'username',
            'first_name',
            'last_name'
        ]

class OrderSerializer(serializers.ModelSerializer):
    user_id = UserRegistrationSerializer()
    gym_id = GymDetailsSerializer()
    product_id = ProductSerializer()
    class Meta:
        model = Orders
        fields = "__all__"