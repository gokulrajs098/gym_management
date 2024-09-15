# products / serializers.py

from rest_framework import serializers
from .models import GymProducts
from gym_details.models import GymDetails
from user_auth.models import CustomUserRegistration
import stripe
from django.conf import settings

# Set your Stripe secret key (from settings)
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    reviews = serializers.CharField(required=True)
    stock = serializers.IntegerField(required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)  # New price field
    Gym = serializers.PrimaryKeyRelatedField(queryset=GymDetails.objects.all(), required=True)
    admin = serializers.PrimaryKeyRelatedField(queryset=CustomUserRegistration.objects.filter(is_staff=True), required=True)
    
    class Meta:
        model = GymProducts
        fields = ['id', 'name', 'type', 'desc', 'image', 'reviews', 'stock', 'price', 'Gym', 'admin', 'stripe_product_id', 'stripe_price_id']
    
    def create(self, validated_data):
        # Create a Stripe Product
        stripe_product = stripe.Product.create(
            name=validated_data['name'],
            description=validated_data['desc'],
        )

        # Create a Stripe Price
        stripe_price = stripe.Price.create(
            product=stripe_product.id,
            unit_amount=int(validated_data['price'] * 100),  # Convert price to cents
            currency='usd',  # Use your preferred currency
        )

        # Save Stripe IDs to the model
        validated_data['stripe_product_id'] = stripe_product.id
        validated_data['stripe_price_id'] = stripe_price.id

        product = GymProducts.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        # Update the product in the local database
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.image = validated_data.get('image', instance.image)
        instance.reviews = validated_data.get('reviews', instance.reviews)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.price = validated_data.get('price', instance.price)  # Update price
        
        # Optional: Update Stripe product/price if needed
        if 'name' in validated_data or 'desc' in validated_data or 'price' in validated_data:
            # Update Stripe Product
            stripe.Product.modify(
                instance.stripe_product_id,
                name=validated_data.get('name', instance.name),
                description=validated_data.get('desc', instance.desc),
            )

            # Update Stripe Price
            stripe.Price.modify(
                instance.stripe_price_id,
                unit_amount=int(validated_data.get('price', instance.price) * 100),  # Convert price to cents
            )

        instance.save()
        return instance