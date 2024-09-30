from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import GymDetails
from .serializers import GymDetailsSerializer
import uuid
from django.shortcuts import get_object_or_404
from user_auth.models import CustomUserRegistration
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
import requests 
import stripe
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(uuid_to_test)
        return True
    except ValueError:
        return False
request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['admin', 'gym_name', 'gym_email', 'admin', 'gym_owner_first_name', 'gym_owner_last_name', 'gym_address', 'gym_phone_number', 'promo_code_offers', 'promo_code'],
    properties={
        'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)'),
        'gym_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the gym'),
        'gym_email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email of the gym'),
        'gym_owner_first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the gym owner'),
        'gym_owner_last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the gym owner'),
        'gym_address': openapi.Schema(type=openapi.TYPE_STRING, description='Address of the gym'),
        'gym_phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the gym'),
        'promo_code_offers': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether promo codes are offered'),
        'promo_code': openapi.Schema(type=openapi.TYPE_STRING, description='Promo code', maxLength=30)
    }
)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve gym details by admin ID. Requires admin privileges.",
    manual_parameters=[
        openapi.Parameter(
            'admin',
            openapi.IN_QUERY,
            description="Admin ID associated with the gym details",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: openapi.Response(
            description="Gym details retrieved successfully",
            schema=GymDetailsSerializer
        ),
        400: openapi.Response(
            description="Bad Request, missing or invalid Admin ID",
            examples={
                "application/json": {
                    "error": "Admin ID is required"
                }
            }
        ),
        404: openapi.Response(
            description="Not Found, Admin ID or Gym Details not found",
            examples={
                "application/json": {
                    "error": "Admin ID not found or not an admin user"
                }
            }
        ),
        500: openapi.Response(
            description="Internal Server Error",
            examples={
                "application/json": {
                    "error": "Unexpected error message"
                }
            }
        )
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Add gym details for a specific admin. Requires admin privileges.",
    request_body=request_body_schema,
    responses={
        201: openapi.Response(
            description="Gym details added successfully"
        ),
        400: openapi.Response(
            description="Bad Request, validation errors or missing Admin ID",
            examples={
                "application/json": {
                    "error": "Admin ID is required"
                }
            }
        ),
        404: openapi.Response(
            description="Not Found, Admin ID not found or not an admin user",
            examples={
                "application/json": {
                    "error": "Admin ID not found or not an admin user"
                }
            }
        )
    }
)
@swagger_auto_schema(
    method='put',
    operation_description="Update gym details for a specific admin. Requires admin privileges.",
    request_body=request_body_schema,
    responses={
        200: openapi.Response(
            description="Gym details updated successfully"
        ),
        400: openapi.Response(
            description="Bad Request, validation errors or missing Admin ID",
            examples={
                "application/json": {
                    "error": "Admin ID is required"
                }
            }
        ),
        404: openapi.Response(
            description="Not Found, Admin ID or Gym Details not found",
            examples={
                "application/json": {
                    "error": "Admin ID not found or not an admin user"
                }
            }
        )
    }
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete gym details for a specific admin. Requires admin privileges.",
    manual_parameters=[
        openapi.Parameter(
            'admin',
            openapi.IN_QUERY,
            description="Admin ID associated with the gym details to delete",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        204: openapi.Response(
            description="Gym details deleted successfully"
        ),
        400: openapi.Response(
            description="Bad Request, missing or invalid Admin ID",
            examples={
                "application/json": {
                    "error": "Admin ID is required"
                }
            }
        ),
        404: openapi.Response(
            description="Not Found, Admin ID or Gym Details not found",
            examples={
                "application/json": {
                    "error": "Admin ID not found or not an admin user"
                }
            }
        )
    }
)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_gym_details(request):
    if request.method == "GET":
        admin_id = request.GET.get('admin')
        try:
            if admin_id:
                # Check if the admin user exists and is a staff member
                admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)

                # Get the first gym detail associated with the admin
                gym = GymDetails.objects.filter(admin_id=admin_id).first()

                if not gym:
                    return Response({"error": "No gym details found for this admin"}, status=status.HTTP_404_NOT_FOUND)

                # Serialize the first gym detail
                serializer = GymDetailsSerializer(gym)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Fetch all gym details if no admin_id is provided
                gyms = GymDetails.objects.all()

                if not gyms:
                    return Response({"error": "No gym details found"}, status=status.HTTP_404_NOT_FOUND)

                # Serialize all gym details
                serializer = GymDetailsSerializer(gyms, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == "POST":
        admin_id = request.data.get('admin')
        if not admin_id:
            return Response({"error": "Admin ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the admin user and ensure it's a staff member
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)

            # Check if a GymDetails entry already exists for this admin
            if GymDetails.objects.filter(admin=admin).exists():
                return Response({"error": "A gym entry already exists for this admin"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the request data
            if 'gym_name' not in request.data:
                return Response({"error": "Gym name is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Pass the request data to the serializer
            serializer = GymDetailsSerializer(data=request.data)

            if serializer.is_valid():
                # Save the gym details, associating with the admin
                serializer.save(admin=admin)
                return Response({"message":"Gym registered successfully"}, status=status.HTTP_201_CREATED)
            else:
                # If serializer validation fails, return the errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        except KeyError as ke:
            # Handle missing field errors
            return Response({"error": f"Missing field: {str(ke)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any other unexpected exceptions and return a generic error response
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            # Handle serializer validation errors more specifically
            return Response({"error": "Validation Error", "details": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any other unexpected exceptions and return a generic error response
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == "PUT":
        admin_id = request.data.get('admin')
        if not admin_id:
            return Response({"error": "Admin ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the admin user exists and is a staff member
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)

            # Get all gym details associated with the admin
            gyms = GymDetails.objects.filter(admin=admin_id)
            
            if not gyms.exists():
                return Response({"error": "No gym details found for the given admin ID"}, status=status.HTTP_404_NOT_FOUND)
            
            # Loop through each gym and update it
            for gym in gyms:
                serializer = GymDetailsSerializer(gym, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # If any gym fails to update, return the errors
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"message": "Gym details updated successfully"}, status=status.HTTP_200_OK)
        
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == "DELETE":
        admin_id = request.GET.get('admin')
        if not admin_id:
            return Response({"error": "Admin ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the admin user exists and is a staff member
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            
            # Get all gym details associated with the admin
            gyms = GymDetails.objects.filter(admin=admin_id)
            
            if not gyms.exists():
                return Response({"error": "No gym details found for the given admin ID"}, status=status.HTTP_404_NOT_FOUND)

            # Delete all the gym details associated with the admin
            gyms.delete()
            
            return Response({"message": "All gym details deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class StripeCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the authorization code from the URL parameters
        code = request.GET.get('code')

        if not code:
            return Response({"error": "No authorization code provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Exchange the authorization code for an access token
            response = requests.post('https://connect.stripe.com/oauth/token', data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:8000/callback',
            }, auth=(settings.STRIPE_TEST_SECRET_KEY, ''))

            response_data = response.json()

            if response.status_code == 200:
                # Extract the access token and other relevant data
                access_token = response_data.get('access_token')
                stripe_user_id = response_data.get('stripe_user_id')
                refresh_token = response_data.get('refresh_token')
                return Response({"access_token": access_token, "stripe_user_id": stripe_user_id, "refresh_token": refresh_token})
            else:
                return Response({"error": f"Error exchanging code for access token: {response_data}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)