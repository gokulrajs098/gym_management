from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserRegistrationSerializer, UserLoginSerializer, AdminRegistrationSerializer, AdminLoginSerializer, SuperUserLoginSerializer,PasswordResetEmailSerializer, PasswordResetSerializer, LogoutSerializer
from .models import CustomUserRegistration
import logging
import jwt
import base64
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
from rest_framework_simplejwt.exceptions import TokenError
from gym_details.models import GymDetails
import uuid
from rest_framework.permissions import BasePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .gmail_service import get_gmail_service
from email.mime.text import MIMEText

SECRET_KEY = ")_^4mxv8-8z$+lq5j%vuu%o09c20mcgs2_fp)3zy*hy9=0wo6("
token_generator = PasswordResetTokenGenerator()
logger = logging.getLogger(__name__)


class IsSuperUserForPost(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            id = request.data.get('id')
            if id is None:
                return False
            try:
                custom_user = CustomUserRegistration.objects.get(id=id)
                return custom_user.is_superuser
            except CustomUserRegistration.DoesNotExist:
                return False
        return True


def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(uuid_to_test)
        return True
    except ValueError:
        return False

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a user by ID",
    responses={200: UserRegistrationSerializer(), 400: 'Bad Request'},
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_QUERY,
            description="UUID of the user",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@swagger_auto_schema(
    method='post',
    operation_description="Register a new user",
    request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'first_name', 'last_name', 'email', 'phone_number', 'country', 'password1', 'password2', 'id'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, minLength=1, pattern='^[\w.@+-]+$'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1),
        'country': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1),
        'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
    },
),
    responses={201: 'User registered successfully', 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing user by ID",
    request_body= openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'first_name', 'last_name', 'email', 'phone_number', 'country', 'password1', 'password2', 'id'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, minLength=1, pattern='^[\w.@+-]+$'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1),
        'country': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1),
        'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1),
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID (UUID)'),
    },
),
    responses={200: 'User details updated successfully', 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete an existing user by ID",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_QUERY,  # Use IN_QUERY or IN_PATH based on your implementation
            description="UUID of the user",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={204: 'User deleted successfully', 400: 'Bad Request'}
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_user_register(request):
    if request.method == "GET":
        admin_uuid = request.GET.get('id')
        if not admin_uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_uuid(admin_uuid):
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

        admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
        
        # Check if the admin is logged in
        if not admin.is_logged_in:
            return Response({"error": "User must be logged in to view details"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminRegistrationSerializer(admin)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "PUT":
        admin_uuid = request.data.get('id')
        if not admin_uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
        
        # Check if the admin is logged in
        if not admin.is_logged_in:
            return Response({"error": "User must be logged in to update details"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminRegistrationSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin details updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        admin_uuid = request.data.get('id')
        if not admin_uuid:
            return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
        
        # Check if the admin is logged in
        if not admin.is_logged_in:
            return Response({"error": "User must be logged in to delete details"}, status=status.HTTP_403_FORBIDDEN)
        
        admin.delete()
        return Response({"message": "Admin deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    return Response({"message":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve an admin user by UUID",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_QUERY,
            description="UUID of the admin",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: AdminRegistrationSerializer,
        400: 'Bad Request',
        401: 'Unauthorized',
        404: 'Not Found'
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Register a new admin. Only accessible to superusers.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            'id', 'username', 'first_name', 'last_name', 
            'email', 'phone_number', 'country', 'password1', 'password2'
        ],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Super User ID (UUID)'),
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                maxLength=150,
                minLength=1,
                pattern='^[\w.@+-]+$',
                description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
            ),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, description='Last name'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254, description='Email address'),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1, description='Phone number'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Country'),
            'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1, description='Password'),
            'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1, description='Confirm Password'),
            'gym_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Gym name'),
            'gym_address': openapi.Schema(type=openapi.TYPE_STRING, minLength=1, description='Gym address'),
            'gym_phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Gym phone number'),
        },
    ),
    responses={
        201: openapi.Schema(type=openapi.TYPE_STRING, description='User registered successfully'),
        400: openapi.Schema(type=openapi.TYPE_STRING, description='Bad Request')
    },
)
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing admin by UUID",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            'id', 'username', 'first_name', 'last_name', 
            'email', 'phone_number', 'country', 'password1', 'password2'
        ],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Admin ID (UUID)'),
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                maxLength=150,
                minLength=1,
                pattern='^[\w.@+-]+$',
                description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
            ),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=150, description='Last name'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, maxLength=254, description='Email address'),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=15, minLength=1, description='Phone number'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Country'),
            'password1': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1, description='Password'),
            'password2': openapi.Schema(type=openapi.TYPE_STRING, writeOnly=True, maxLength=20, minLength=1, description='Confirm Password'),
            'gym_name': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Gym name'),
            'gym_address': openapi.Schema(type=openapi.TYPE_STRING, minLength=1, description='Gym address'),
            'gym_phone_number': openapi.Schema(type=openapi.TYPE_STRING, maxLength=20, minLength=1, description='Gym phone number'),
        },
    ),
    responses={
        200: 'Admin details updated successfully',
        400: 'Bad Request',
        404: 'Not Found'
    }
)
@swagger_auto_schema(
    method='delete',
    operation_description="Delete an existing admin by UUID",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_QUERY,
            description="UUID of the admin",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        204: 'Admin deleted successfully',
        400: 'Bad Request',
        404: 'Not Found'
    }
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_admin_register(request):
    permission = IsSuperUserForPost()
    if request.method == 'POST' and not permission.has_permission(request, manage_admin_register):
        return Response({"error": "Only superusers can create admins"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == "GET":
        if 'id' in request.GET:
            admin_uuid = request.GET.get('id')
            if not admin_uuid:
                return Response({"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not validate_uuid(admin_uuid):
                return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
            
            admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
            serializer = AdminRegistrationSerializer(admin)
            return Response(serializer.data)
        else:
            return Response({"message":"Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == "POST":
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PUT":
        if 'id' in request.data:
            admin_uuid = request.data.get('id')
            admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
            serializer = AdminRegistrationSerializer(admin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Admin details updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        if 'id' in request.data:
            admin_uuid = request.data.get('id')
            admin = get_object_or_404(CustomUserRegistration, id=admin_uuid)
            admin.delete()
            return Response({"message": "Admin deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Admin UUID is required"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="User login endpoint to authenticate and receive tokens.",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "user_id": "user_id",
                    "is_logged_in": True
                }
            }
        ),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user_id = str(user.pk)
        user = CustomUserRegistration.objects.get(id=user_id)
        user.is_logged_in = True
        user.save()
        return Response({
            "message": "Login successful",
            "user_id": user_id,
            "is_logged_in": True
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Admin login endpoint to authenticate and receive tokens.",
    request_body=AdminLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "user_id": "user_id",
                    "gym_id": "gym_id",
                    "is_logged_in": True
                }
            }
        ),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def admin_login(request):
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.validated_data['user']
            user_id = str(user.pk)
            user = CustomUserRegistration.objects.get(id=user_id)
            user.is_logged_in = True
            user.save()

            try:
                gym = GymDetails.objects.get(admin=user)
                gym_id = gym.id
            except GymDetails.DoesNotExist:
                gym_id = None  # Handle the case where the gym does not exist

            return Response({
                "message": "Login successful",
                "user_id": user_id,
                "gym_id": gym_id,
                "is_logged_in": True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@swagger_auto_schema(
    method='post',
    operation_description="Log in as a superuser to obtain access and refresh tokens.",
    request_body=SuperUserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "access_token": "new_access_token",
                    "refresh_token": "new_refresh_token",
                    "user_id": "user_id",
                    "access_token_expires_in": 600,  # 10 minutes in seconds
                    "refresh_token_expires_in": 604800  # 7 days in seconds
                }
            }
        ),
        400: openapi.Response(
            description="Bad request, validation errors",
            examples={
                "application/json": {
                    "error": "Detailed validation errors"
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden, only superusers can log in here",
            examples={
                "application/json": {
                    "error": "Only superusers can log in here"
                }
            }
        )
    }
)
@api_view(['POST'])
def superuser_login(request):
    serializer = SuperUserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        if not user.is_superuser:
            return Response({"error": "Only superusers can log in here"}, status=status.HTTP_403_FORBIDDEN)
        else:
            
            
            user_id = str(user.pk)
            user = CustomUserRegistration.objects.get(id=user_id)
            user.is_logged_in = True
            user.save()

            return Response({
                "message": "Login successful",
                "user_id": user_id,
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Logs out a user by setting the 'is_logged_in' status to False.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the user to log out')
        },
        required=['user_id']
    ),
    responses={
        200: openapi.Response(
            description="User logged out successfully",
            examples={
                "application/json": {
                    "message": "User logged out successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request, user was not logged in",
            examples={
                "application/json": {
                    "message": "User was not logged in"
                }
            }
        ),
        404: openapi.Response(
            description="User not found",
            examples={
                "application/json": {
                    "message": "User not found"
                }
            }
        )
    }
)
@api_view(['POST'])
def logout_view(request):
    try:
        user_id = request.data.get('user_id')
        user = CustomUserRegistration.objects.get(id=user_id)
        
        if user.is_logged_in:
            user.is_logged_in = False
            user.save()
            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User was not logged in"}, status=status.HTTP_400_BAD_REQUEST)
    
    except CustomUserRegistration.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetEmailSerializer,
    responses={200: 'Password reset link sent', 404: 'Invalid email', 500: 'Internal server error'}
)
@api_view(['POST'])
def send_password_reset_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Try to find the user by email
        user = CustomUserRegistration.objects.get(email=email)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Invalid email'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error querying user by email: {str(e)}")
        return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # Generate password reset token and UID
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(reverse('password-reset-confirm', args=[uid, token]))

        # Create the email content
        message = MIMEText(f'Click the link to reset your password: {reset_link}')
        message['to'] = email
        message['subject'] = 'Password Reset Request'
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send email via Gmail OAuth
        service = get_gmail_service()
        message = {'raw': raw_message}
        service.users().messages().send(userId='me', body=message).execute()

        return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetSerializer,
    responses={200: 'Password has been reset', 400: 'Invalid token or user', 500: 'Internal server error'}
)
@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUserRegistration.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUserRegistration.DoesNotExist) as e:
        logger.error(f"Error decoding user or fetching user: {str(e)}")
        return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if token_generator.check_token(user, token):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return Response({'error': 'Failed to reset password'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
