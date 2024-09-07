from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import MentorSerializer, MentorLoginSerializer
from .models import Mentors
from user_auth.models import CustomUserRegistration
import uuid
import jwt
from datetime import timedelta, datetime
from gym_details.models import GymDetails

SECRET_KEY = ")_^4mxv8-8z$+lq5j%vuu%o09c20mcgs2_fp)3zy*hy9=0wo6("

def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(uuid_to_test)
        return True
    except ValueError:
        return False

@swagger_auto_schema(
    method='get',
    operation_description="Fetch mentor details based on Admin ID, Mentor ID, or Gym ID.",
    manual_parameters=[
        openapi.Parameter('admin', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid', description='Admin ID (UUID)'),
        openapi.Parameter('mentor_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid', description='Mentor ID (UUID)'),
        openapi.Parameter('gym_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid', description='Gym ID (UUID)')
    ],
    responses={
        200: "Success",
        400: "Bad Request",
        404: "Not Found",
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new mentor",
    request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['admin', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', ',mentor_id', 'expertise'],
    properties={
        'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'expertise': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1),
        'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Gym ID (UUID)'),
    },
),
    responses={
        201: 'Mentor created successfully',
        400: 'Bad Request'
    }
)
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing mentor",
    request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['admin', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', ',mentor_id', 'expertise'],
    properties={
        'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'expertise': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1),
        'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'mentor_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID (UUID)'),
        'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Gym ID (UUID)'),
    },
),
    responses={
        200: 'Mentor updated successfully',
        400: 'Bad Request',
        404: 'Mentor not found'
    }
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a mentor by Mentor ID if associated with the given Admin ID.",
    manual_parameters=[
        openapi.Parameter('admin', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid', description='Admin ID (UUID)'),
        openapi.Parameter('mentor_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='uuid', description='Mentor ID (UUID)')
    ],
    responses={
        204: "Product deleted successfully",
        400: "Bad Request",
        404: "Not Found"
    }
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_mentor(request):
    if request.method =="GET":
        gym_id = request.query_params.get('gym_id')
        admin_id = request.query_params.get('admin')
        mentor_id = request.query_params.get('mentor_id')

        try:
            # Verify the existence of gym_id
            if gym_id and not GymDetails.objects.filter(id=gym_id).exists():
                return Response({"error": "Gym ID not found"}, status=status.HTTP_404_NOT_FOUND)

            # Verify the existence of admin_id
            if admin_id and not CustomUserRegistration.objects.filter(id=admin_id, is_staff=True).exists():
                return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

            # Verify the existence of mentor_id
            if mentor_id and not Mentors.objects.filter(id=mentor_id).exists():
                return Response({"error": "Mentor ID not found"}, status=status.HTTP_404_NOT_FOUND)

            if mentor_id:
                # Fetch a specific mentor
                mentor = get_object_or_404(Mentors, id=mentor_id)
                serializer = MentorSerializer(mentor)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if admin_id and gym_id:
                # Fetch mentors for a specific gym and admin
                admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
                gym = GymDetails.objects.get(id=gym_id, admin=admin)
                mentors = get_list_or_404(Mentors, Gym=gym, admin=admin)
                serializer = MentorSerializer(mentors, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if gym_id:
                # Fetch mentors for a specific gym
                gym = GymDetails.objects.get(id=gym_id)
                mentors = get_list_or_404(Mentors, Gym=gym)
                serializer = MentorSerializer(mentors, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # If no query parameters are provided, return an error
            return Response({"error": "At least one query parameter (gym_id, admin, or mentor_id) is required"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    elif request.method == "POST":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')
        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            gym = GymDetails.objects.get(id=gym_id, admin=admin)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except GymDetails.DoesNotExist:
            return Response({"error": "Gym ID not found for the given admin"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        data['Gym'] = gym_id
        serializer = MentorSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Mentor added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "PUT":
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')
        mentor_id = request.data.get('mentor_id')
        if not admin_id or not gym_id or not mentor_id:
            return Response({"error": "Admin ID, Gym ID, and Product ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            gym = GymDetails.objects.get(id=gym_id, admin=admin)
            mentor = get_object_or_404(Mentors, admin_id=admin_id, Gym=gym, id=mentor_id)
            
            serializer = MentorSerializer(mentor, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Mentor details updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except GymDetails.DoesNotExist:
            return Response({"error": "Gym ID not found for the given admin"}, status=status.HTTP_404_NOT_FOUND)
        except Mentors.DoesNotExist:
            return Response({"error": "Product ID not found for the given admin and gym"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == "DELETE":
        admin_id = request.GET.get('admin')
        mentor_id = request.GET.get('mentor_id')

        if not admin_id or not mentor_id:
            return Response({"error": "Admin ID and Mentor ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify if the admin exists and is a staff member
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            
            # Verify if the mentor exists and is associated with the admin
            mentor = Mentors.objects.get(id=mentor_id, admin=admin)
            
            # Delete the mentor
            mentor.delete()
            return Response({"message": "Mentor deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Mentors.DoesNotExist:
            return Response({"error": "Mentor ID not found for the given admin"}, status=status.HTTP_404_NOT_FOUND)
            
@swagger_auto_schema(
    method='post',
    request_body=MentorLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "access_token": "string",
                    "refresh_token": "string",
                    "mentor_id": "string",
                    "access_token_expires_in": 600,
                    "refresh_token_expires_in": 604800
                }
            }
        ),
        400: openapi.Response(
            description="Invalid credentials or other errors",
            examples={
                "application/json": {
                    "username": ["This field is required."],
                    "password": ["This field is required."],
                }
            }
        ),
    }
)
@api_view(['POST'])
def mentor_login(request):
    serializer = MentorLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user_id = str(user.pk)

        access_token_payload = {
            'user_id': user_id, 
            'exp': int((datetime.now() + timedelta(minutes=10)).timestamp())
        }
        access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

        refresh_token_payload = {
            'user_id': user_id, 
            'type': 'refresh',
            'exp': int((datetime.now() + timedelta(days=7)).timestamp())
        }
        refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "mentor_id": user_id,
            "access_token_expires_in": 600, 
            "refresh_token_expires_in": 604800  
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
        },
        required=['refresh_token']
    ),
    responses={
        200: openapi.Response(
            description="Token refresh successful",
            examples={
                "application/json": {
                    "access_token": "string",
                    "refresh_token": "string",
                    "access_token_expires_in": 600,
                    "refresh_token_expires_in": 604800
                }
            }
        ),
        400: openapi.Response(
            description="Missing or invalid refresh token",
            examples={
                "application/json": {
                    "error": "Refresh token is required"
                }
            }
        ),
        401: openapi.Response(
            description="Invalid or expired refresh token",
            examples={
                "application/json": {
                    "error": "Refresh token has expired"  # Or "Invalid refresh token"
                }
            }
        ),
    }
)
@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
        user = Mentors.objects.get(pk=decoded['user_id'])
        user_id = str(user.pk)
        new_access_token = jwt.encode({
            'user_id': user_id,
            'exp': int((datetime.now() + timedelta(minutes=10)).timestamp())
        }, SECRET_KEY, algorithm='HS256')
        new_refresh_token = jwt.encode({
            'user_id': user_id,
            'type': 'refresh',
            'exp': int((datetime.now() + timedelta(days=7)).timestamp())
        }, SECRET_KEY, algorithm='HS256')
        return Response({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "access_token_expires_in": 600,  # Ensure the correct duration in seconds
            "refresh_token_expires_in": 604800
        }, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response({"error": "Refresh token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)