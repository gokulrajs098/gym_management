from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_fcm_notification

@api_view(['POST'])
def send_notifications(request):
    admin_id = request.data.get('admin_id')
    gym_id = request.data.get('gym_id')
    try:
        token = request.data.get('token')
        title = request.data.get('title')
        body = request.data.get('body')


        send_fcm_notification(token, title, body)

        return Response({'status':"Notification sent!"})
    except Exception as e:
        return Response({"error":e}, status=500)