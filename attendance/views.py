from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import GymAttendance
from .serializers import GymAttendanceSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from user_auth.models import CustomUserRegistration
from gym_details.models import GymDetails
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user', 'gym'],
        properties={
        'user': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description='User ID'
        ),
        'gym': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description='Gym ID'
        ),
    }
    ),
    responses={
        200: openapi.Response('Checked in successfully'),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('Not Found'),
    }
)
@api_view(['POST'])
def check_in(request):
    user_id = request.data.get('user')
    gym_id = request.data.get('gym')

    if not user_id or not gym_id:
        return Response({"error": "User ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(CustomUserRegistration, id=user_id)
        gym = get_object_or_404(GymDetails, id=gym_id)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    attendance, created = GymAttendance.objects.get_or_create(user=user, gym=gym, checked_in=False)

    if not created:
        return Response({"error": "User is already checked in"}, status=status.HTTP_400_BAD_REQUEST)

    attendance.check_in_time = timezone.now()
    attendance.checked_in = True
    attendance.save()

    return Response({"message": "Checked in successfully"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user', 'gym'],
        properties={
        'user': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description='User ID'
        ),
        'gym': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description='Gym ID'
        ),
    }
    ),
    responses={
        200: openapi.Response('Checked out successfully'),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('Not Found'),
    }
)
@api_view(['POST'])
def check_out(request):
    user_id = request.data.get('user')
    gym_id = request.data.get('gym')

    if not user_id or not gym_id:
        return Response({"error": "User ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(CustomUserRegistration, id=user_id)
        gym = get_object_or_404(GymDetails, id=gym_id)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    try:
        attendance = GymAttendance.objects.get(user=user, gym=gym, checked_in=True)
    except GymAttendance.DoesNotExist:
        return Response({"error": "User has not checked in"}, status=status.HTTP_400_BAD_REQUEST)

    attendance.check_out_time = timezone.now()
    attendance.checked_in = False
    attendance.save()

    return Response({"message": "Checked out successfully"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('gym', openapi.IN_QUERY, description="Gym ID", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('user', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: GymAttendanceSerializer(many=True),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('Not Found'),
    }
)
@api_view(['GET'])
def get_attendance(request):
    gym_id = request.GET.get('gym')
    user_id = request.GET.get('user')  # Optional parameter

    if not gym_id:
        return Response({"error": "Gym ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        get_object_or_404(GymDetails, id=gym_id)
    except GymDetails.DoesNotExist:
        return Response({"error": "Gym ID not found in GymDetails"}, status=status.HTTP_404_NOT_FOUND)

    if user_id:
        # Verify user
        try:
            get_object_or_404(CustomUserRegistration, id=user_id)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "User ID not found in CustomUserRegistration"}, status=status.HTTP_404_NOT_FOUND)

        attendances = GymAttendance.objects.filter(gym=gym_id, user_id=user_id)
    else:
        attendances = GymAttendance.objects.filter(gym=gym_id)

    # Serialize and return the attendance data with nested details
    serializer = GymAttendanceSerializer(attendances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)