from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import EventSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from gym_details.models import GymDetails
from user_auth.models import CustomUserRegistration

@swagger_auto_schema(
    method='post',
    operation_description="Add a new event. Requires admin privileges.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'date', 'timing', 'location', 'description', 'gym_id', 'admin_id'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the event'),
            'date': openapi.Schema(type=openapi.TYPE_STRING, description='Date of the event'),
            'timing': openapi.Schema(type=openapi.TYPE_STRING, description='Timing of the event'),
            'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location of the event'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the event'),
            'Guest_name': openapi.Schema(type=openapi.TYPE_STRING, description='guest of the event'),
            'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Gym ID associated with the event'),
            'admin_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Admin ID associated with the event'),
        }
    ),
    responses={
        201: "Event added successfully",
        400: "Bad Request, validation errors or missing parameters",
        404: "Not Found, Gym or admin not found"
    }
)
@api_view(['POST'])
def add_event(request):
    gym_id = request.data.get('gym_id')
    admin_id = request.data.get('admin_id')

    try:
        admin_user = CustomUserRegistration.objects.get(id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin is not associated with CustomUserRegistration'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gym = get_object_or_404(GymDetails, id=gym_id)
    except GymDetails.DoesNotExist:
        return Response({'error': 'Gym ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        admin = get_object_or_404(CustomUserRegistration, id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    request.data['gym'] = gym_id  # Set the gym ID directly in the request data

    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the event without passing gym object explicitly
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@swagger_auto_schema(
    method='put',
    operation_description="Update an event. Requires admin privileges.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['event_id', 'name', 'date', 'timing', 'location', 'description', 'gym_id', 'admin_id'],
        properties={
            'event_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Event ID'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the event'),
            'date': openapi.Schema(type=openapi.TYPE_STRING, description='Date of the event'),
            'timing': openapi.Schema(type=openapi.TYPE_STRING, description='Timing of the event'),
            'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location of the event'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the event'),
            'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Gym ID associated with the event'),
            'admin_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Admin ID associated with the event'),
        }
    ),
    responses={
        200: "Event updated successfully",
        400: "Bad Request, validation errors or missing parameters",
        404: "Not Found, Event ID is invalid"
    }
)
@api_view(['PUT'])
def update_event(request):
    event_id = request.data.get('event_id')
    gym_id = request.data.get('gym_id')
    admin_id = request.data.get('admin_id')

    try:
        event = get_object_or_404(Event, id=event_id)
    except Event.DoesNotExist:
        return Response({'error': 'Event ID is invalid'}, status=status.HTTP_404_NOT_FOUND)

    try:
        admin_user = CustomUserRegistration.objects.get(id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin is not associated with CustomUserRegistration'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gym = get_object_or_404(GymDetails, id=gym_id)
    except GymDetails.DoesNotExist:
        return Response({'error': 'Gym ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        admin = get_object_or_404(CustomUserRegistration, id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    request.data['gym'] = gym_id  # Set the gym ID directly in the request data
    request.data.pop('event_id', None)  # Remove event_id from the request data

    serializer = EventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  # Save the event without passing gym object explicitly
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve events for a specific gym.",
    manual_parameters=[
        openapi.Parameter('gym_id', openapi.IN_PATH, type=openapi.TYPE_STRING, format="uuid", required=True, description='Gym ID'),
    ],
    responses={
        200: "Events retrieved successfully",
        404: "Not Found, Gym ID is invalid"
    }
)
@api_view(['GET'])
def view_events_by_gym(request, gym_id):
    # Verify gym ID
    try:
        gym = get_object_or_404(GymDetails, id=gym_id)
    except GymDetails.DoesNotExist:
        return Response({'error': 'Gym ID is invalid'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve events for the specified gym
    events = Event.objects.filter(gym=gym)

    # Serialize the events
    serializer = EventSerializer(events, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='delete',
    operation_description="Delete an event. Requires admin privileges.",
    manual_parameters=[
        openapi.Parameter('event_id', openapi.IN_PATH, type=openapi.TYPE_STRING, format="uuid", required=True, description='Event ID'),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['admin_id'],
        properties={
            'admin_id': openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description='Admin ID associated with the event'),
        }
    ),
    responses={
        200: "Event deleted successfully",
        400: "Bad Request, validation errors or missing parameters",
        404: "Not Found, Event ID is invalid"
    }
)
@api_view(['DELETE'])
def delete_event(request, event_id):
    try:
        event = get_object_or_404(Event, id=event_id)
    except Event.DoesNotExist:
        return Response({'error': 'Event ID is invalid'}, status=status.HTTP_404_NOT_FOUND)
    
    admin_id = request.data.get('admin_id')
    try:
        admin_user = CustomUserRegistration.objects.get(id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin is not associated with CustomUserRegistration'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin = get_object_or_404(CustomUserRegistration, id=admin_id)
    except CustomUserRegistration.DoesNotExist:
        return Response({'error': 'Admin ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    event.delete()
    return Response({'message': 'Event deleted successfully'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all events.",
    responses={
        200: "Events retrieved successfully",
    }
)
@api_view(['GET'])
def view_all_events(request):
    # Retrieve all events if no gym ID is provided
    events = Event.objects.all()

    # Serialize the events
    serializer = EventSerializer(events, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)