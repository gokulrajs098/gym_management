from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import uuid
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import CustomerSerializer
from user_auth.models import CustomUserRegistration
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from gym_details.models import GymDetails

customer_request_body_schema = openapi.Schema(
    title='Customer Request Body',
    type=openapi.TYPE_OBJECT,
    properties={
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID (UUID)'),
        'plan_name': openapi.Schema(type=openapi.TYPE_STRING, description='Plan Name'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'plan_status': openapi.Schema(type=openapi.TYPE_STRING, description='Plan Status', enum=['active', 'inactive']),  # Adjust choices as per STATUS_CHOICES
        'plan_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Plan Start Date'),
        'plan_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Plan End Date'),
        'gym': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Gym ID (UUID)'),
        'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)')
    },
    required=['user', 'first_name', 'last_name', 'username', 'plan_status', 'plan_start_date', 'plan_end_date', 'gym']  # Mark required fields here
)

customer_request_body_schema_put = openapi.Schema(
    title='Customer Request Body',
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='ID (UUID)'),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID (UUID)'),
        'plan_name': openapi.Schema(type=openapi.TYPE_STRING, description='Plan Name'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'plan_status': openapi.Schema(type=openapi.TYPE_STRING, description='Plan Status', enum=['active', 'inactive']),  # Adjust choices as per STATUS_CHOICES
        'plan_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Plan Start Date'),
        'plan_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Plan End Date'),
        'gym': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Gym ID (UUID)'),
        'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)')
    },
    required=['user', 'first_name', 'last_name', 'username', 'plan_status', 'plan_start_date', 'plan_end_date', 'gym']  # Mark required fields here
)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description="UUID of the user to fetch details from Customer model",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=False
        ),
        openapi.Parameter(
            'admin',
            openapi.IN_QUERY,
            description="UUID of the Admin to verify and get associated details",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=False
        ),
        openapi.Parameter(
            'gym_id',
            openapi.IN_QUERY,
            description="UUID of the Gym to verify and get associated details",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('Success', CustomerSerializer(many=True)),
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error"
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new customer",
    request_body=customer_request_body_schema,
    responses={
        201: 'Customer created successfully',
        400: 'Bad Request'
    }
)
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing customer",
    request_body=customer_request_body_schema_put,
    responses={
        200: 'Customer updated successfully',
        400: 'Bad Request',
        404: 'Not Found'
    }
)
@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, description="User ID (UUID)", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        openapi.Parameter('admin', openapi.IN_QUERY, description="Admin ID (UUID)", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
    ],
    responses={
        204: openapi.Response('Customer detail deleted successfully'),
        400: openapi.Response('Bad Request - User ID and Admin ID are required'),
        403: openapi.Response('Forbidden - Customer does not belong to the specified gym and admin'),
        404: openapi.Response('Not Found - Admin ID not found or not an admin user, or Customer not found for the provided User ID'),
        500: openapi.Response('Internal Server Error - Unexpected error occurred')
    }
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_customer(request):
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        admin_id = request.GET.get('admin')
        gym_id = request.GET.get('gym_id')

        if user_id:
            try:
                # Fetch and return details for the user
                user = get_object_or_404(Customer, user_id=user_id)
                serializer = CustomerSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Customer.DoesNotExist:
                return Response({"error": "User ID not found in Customer model"}, status=status.HTTP_404_NOT_FOUND)
        
        if admin_id and gym_id:
            try:
                # Verify admin
                admin = get_object_or_404(CustomUserRegistration, id=admin_id, is_staff=True)
                
                # Verify gym details
                gym = get_object_or_404(GymDetails, id=gym_id)

                # Fetch customer details for the gym
                customer_details = Customer.objects.filter(gym_id=gym_id)
                
                # Serialize the data
                serializer = CustomerSerializer(customer_details, many=True)
                
                # Return the response
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except Exception as e:
                # Handle any exceptions that may occur during the process
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == "POST":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(data=request.data)
        gym = GymDetails.objects.get(id = gym_id)
        if serializer.is_valid():
            serializer.save(gym=gym)
            return Response({"message": "Customer details added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym')
        id = request.data.get('id')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            customer = get_object_or_404(Customer, id=id)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Customer details updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"error": "Gym detail not found for the given Gym ID and Admin ID"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == "DELETE":
        user_id = request.data.get('user_id')
        admin_id = request.data.get('admin')

        if not user_id or not admin_id:
            return Response({"error": "User ID and Admin ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the admin is valid and has the required permissions
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)

            # Fetch the customer object using the user_id
            customer = get_object_or_404(Customer, id=user_id)

            # Check if the customer is associated with the gym and admin
            if customer.gym.admin_id != admin_id:
                return Response({"error": "Customer does not belong to the specified gym and admin"}, status=status.HTTP_403_FORBIDDEN)

            # Delete the customer object
            customer.delete()
            return Response({"message": "Customer detail deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found for the provided User ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)