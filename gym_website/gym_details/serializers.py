# gym_details/serializers.py
from rest_framework import serializers
from .models import GymDetails
from user_auth.serializers import AdminRegistrationSerializer
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
class GymDetailsSerializer(serializers.ModelSerializer):
    admin = AdminRegistrationSerializer(read_only=True)

    class Meta:
        model = GymDetails
        fields = ['gym_name', 'gym_owner_first_name', 'gym_owner_last_name', 'gym_address', 'gym_phone_number', 'gym_email', 'admin']
    client_id = 'ca_QjwlKtQ5NP4fSeo5O0EuVAHm6MNEA7TC'
    def create(self, validated_data):
        gym_name = validated_data['gym_name']
        gym_email = validated_data['gym_email']
        admin = validated_data['admin']
        gym_owner_first_name = validated_data['gym_owner_first_name']
        gym_owner_last_name = validated_data['gym_owner_last_name']
        gym_address = validated_data['gym_address']
        gym_phone_number = validated_data['gym_phone_number']
        client_id = 'ca_QjwlKtQ5NP4fSeo5O0EuVAHm6MNEA7TC'

        try:
            # Create the Stripe account
            account = stripe.Account.create(
                type='standard',
                country='US',
                email=gym_email,
                business_type='company',
                business_profile={
                    'name': gym_name,
                    'url': 'https://your-platform-url.com',
                
                },
            )

            # Create an Account Link for onboarding
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url='https://example.com/reauth',
                return_url='https://example.com/return',
                type='account_onboarding',
            )

            # Generate the OAuth URL using the Client ID
            redirect_uri = "http://localhost:8000/gyms/callback"
            connect_url = f"https://connect.stripe.com/oauth/authorize?response_type=code&client_id={client_id}&scope=read_write&redirect_uri={redirect_uri}"

            # Create the gym details object
            gym = GymDetails.objects.create(
                gym_name=gym_name,
                gym_email=gym_email,
                stripe_account_id=account.id,
                admin=admin,
                gym_owner_first_name=gym_owner_first_name,
                gym_owner_last_name=gym_owner_last_name,
                gym_address=gym_address,
                gym_phone_number=gym_phone_number
            )

            # Return the onboarding URL and connect URL
            return {'onboarding_url': account_link.url, 'connect_url': connect_url, 'stripe_account_id': account.id}

        except stripe.error.StripeError as e:
            raise serializers.ValidationError({'error': str(e)})


    def update(self, instance, validated_data):
        # Check if instance is a dictionary
        if isinstance(instance, dict):
            instance.update(validated_data)
            return instance
        
        # Handle instance as a model
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance