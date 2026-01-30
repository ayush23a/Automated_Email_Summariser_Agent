import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(settings.GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(settings.GMAIL_TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                 creds.refresh(Request())
            except Exception:
                 # If refresh fails, delete token and try again
                 if os.path.exists(settings.GMAIL_TOKEN_PATH):
                     os.remove(settings.GMAIL_TOKEN_PATH)
                 creds = None
        
        if not creds:
            if not os.path.exists(settings.GMAIL_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Credentials file not found at {settings.GMAIL_CREDENTIALS_PATH}. "
                    "Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(settings.GMAIL_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service
