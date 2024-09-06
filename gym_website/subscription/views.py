from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import SubscriptionSerializer
from .models import SubscriptionPlan
from user_auth.models import CustomUserRegistration
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from gym_details.models import GymDetails

def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(uuid_to_test)
        return True
    except ValueError:
        return False

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve subscription details for a specific gym. Requires Admin ID and Gym ID.",
    manual_parameters=[
        openapi.Parameter('admin', openapi.IN_QUERY, description="Admin ID", type=openapi.TYPE_STRING),
        openapi.Parameter('gym_id', openapi.IN_QUERY, description="Gym ID", type=openapi.TYPE_STRING),
    ],
    responses={
        200: SubscriptionSerializer,
        400: 'Bad Request',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="creating a subscription plan. Requires Admin ID and Gym ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plan_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the plan'),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the plan'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Price of the plan'),
                'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the admin (optional)', nullable=True),
                'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the gym (optional)', nullable=True),
                'interval': openapi.Schema(type=openapi.TYPE_STRING, description='Interval for the plan')
            },
            required=['plan_name', 'desc', 'price','gym', 'interval', 'admin']
        )
    )
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing subscription plan. Requires Admin ID and Gym ID.",
     request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plan_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the plan'),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the plan'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Price of the plan'),
                'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the admin (optional)', nullable=True),
                'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the gym (optional)', nullable=True),
                'interval': openapi.Schema(type=openapi.TYPE_STRING, description='Interval for the plan')
            },
            required=['plan_name', 'desc', 'price','gym', 'interval', 'admin']
        )
    )
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a subscription plan. Requires Admin ID and Gym ID.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['admin', 'gym_id'],
        properties={
            'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the admin (optional)', nullable=True),
            'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the gym (optional)', nullable=True),
        }
    ),
    responses={
        204: 'Subscription plan detail deleted successfully',
        400: 'Bad Request',
        404: 'Not Found'
    }
)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_subscriptions(request):
    if request.method == "GET":
        gym_id = request.GET.get('gym_id')

        if not gym_id:
            return Response({"error": "Gym ID id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            gym = get_object_or_404(SubscriptionPlan, gym=gym_id)
            serializer = SubscriptionSerializer(gym)
            return Response(serializer.data)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription detail not found for the given Gym ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == "POST":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        # Check if a subscription already exists for the given admin_id and gym_id
        if SubscriptionPlan.objects.filter(admin=admin, gym=gym_id).exists():
            return Response({"error": "A subscription plan for this gym by this admin already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # If no existing subscription, proceed to create a new one
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            gym = get_object_or_404(GymDetails, id=gym_id)
            # Pass the admin and gym as keyword arguments
            serializer.save(admin=admin, gym=gym)
            return Response({"message": "Subscription plan details added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        # Find the subscription object to update
        try:
            subscription = SubscriptionPlan.objects.get(gym=gym_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription not found for this gym"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)  # Use partial=True for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Subscription plan details updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        try:
            gym = SubscriptionPlan.objects.get(admin_id=admin_id, gym_id=gym_id)
            gym.delete()
            return Response({"message": "Subscription plan detail deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription detail not found for the given Gym ID"}, status=status.HTTP_404_NOT_FOUND)