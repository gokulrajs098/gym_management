from rest_framework import serializers
from .models import SubscriptionPlan
import stripe

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"

    def validate(self, attrs):
        required_fields = ['admin','desc', 'plan_name', 'price', 'interval', 'interval_count']
        missing_fields = [field for field in required_fields if field not in attrs or attrs[field] == '']

        if missing_fields:
            raise serializers.ValidationError({field: 'This field is required.' for field in missing_fields})
        return attrs

    def create(self, validated_data):

        product = SubscriptionPlan.objects.create(**validated_data)


        stripe_product = stripe.Product.create(
            name=product.plan_name,
            description=product.desc,
        )

     
        stripe_price = stripe.Price.create(
            product=stripe_product.id,
            unit_amount=int(product.price * 100),  
            currency='usd', 
            recurring={
        "interval": product.interval,  # Use the interval input (e.g., 'month' or 'year')
        "interval_count": product.interval_count  # Use interval_count (e.g., every 3 months)
    },

        )

        product.stripe_product_id = stripe_product.id
        product.stripe_price_id = stripe_price.id
        product.save()
        
        return product

    def update(self, instance, validated_data):
        instance.plan_name = validated_data.get('plan_name', instance.plan_name)
        instance.price = validated_data.get('price', instance.price)
        return instance