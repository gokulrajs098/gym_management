from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_fcm_notification
from user_auth.models import CustomUserRegistration
from customers.models import Customer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
    method='post',
    operation_summary="Send Notifications",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'admin_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the admin'),
            'gym_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the gym'),
            'to': openapi.Schema(type=openapi.TYPE_STRING, description='Specify "users" or "customers"'),
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Notification title'),
            'body': openapi.Schema(type=openapi.TYPE_STRING, description='Notification body'),
        },
    ),
    responses={
        200: openapi.Response('Notification sent successfully'),
        404: openapi.Response('Admin or customers not found'),
        500: openapi.Response('Internal server error'),
    }
)
@api_view(['POST'])
def send_notifications(request):
    admin_id = request.data.get('admin_id')
    gym_id = request.data.get('gym_id')
    to = request.data.get('to')
    title = request.data.get('title')
    body = request.data.get('body')
    try:
        if not CustomUserRegistration.objects.filter(id = admin_id, is_staff=True).exists():
            return Response({"messaage":"No admin with that user_id present"}, status=404)
        
        if to == "users":
            users = CustomUserRegistration.objects.all()
            tokens = []
            for user in users:
                tokens += user.fcm_token
            
            for token in tokens:
                send_fcm_notification(token, title, body)
            return Response({'status':"Notification sent!"})
            
        elif to == "customers":
           
            customers = Customer.objects.filter(gym=gym_id)
            if not customer.exists():
                return Response({"message":"No customer associated with this gym_id"})
            tokens = []

            for customer in customers:
                tokens += customer.fcm_token
            for token in tokens:
                send_fcm_notification(token, title, body)
            return Response({'status':"Notification sent!"})

        
    except Exception as e:
        return Response({"error":str(e)}, status=500)
    
@swagger_auto_schema(
    method='post',
    operation_summary="Add FCM Token for User",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
            'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='FCM token of the user'),
        },
    ),
    responses={
        200: openapi.Response('Token added successfully'),
        404: openapi.Response('User not found'),
        500: openapi.Response('Internal server error'),
    }
)
@api_view(['POST'])
def add_token_user(request):
    user_id = request.data.get('user_id')
    fcm_token = request.data.get('fcm_token')
    try:
        user = CustomUserRegistration.objects.get(id = user_id)
        if not user:
            return Response({"message":"user does not exist"}, status=404)
        user.fcm_token = fcm_token
        user.save()
    except Exception as e:
        return Response({str(e)}, status=500)
    
@swagger_auto_schema(
    method='post',
    operation_summary="Add FCM Token for Customer",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the customer'),
            'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='FCM token of the customer'),
        },
    ),
    responses={
        200: openapi.Response('Token added successfully'),
        404: openapi.Response('Customer not found'),
        500: openapi.Response('Internal server error'),
    }
)
@api_view(['POST'])
def add_token_customer(request):
    user_id = request.data.get('customer_id')
    fcm_token = request.data.get('fcm_token')
    try:
        Customer = Customer.objects.get(id = user_id)
        if not Customer:
            return Response({"message":"Customer does not exist"}, status=404)
        Customer.fcm_token = fcm_token
        Customer.save()
    except Exception as e:
        return Response({str(e)}, status=500)
