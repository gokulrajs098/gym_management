import firebase_admin
from firebase_admin import messaging

def send_fcm_notification(token, title, body):
    message = messaging.Message(
        
    )