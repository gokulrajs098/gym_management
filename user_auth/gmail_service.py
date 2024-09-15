import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_gmail_service():
    creds = None

    # Read credentials from environment variables
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

    # Create credentials object
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri='https://oauth2.googleapis.com/token'
    )


    # Build and return the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service
