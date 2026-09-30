
# Google Auth imports
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os


# # --- 1. GMAIL OAUTH2 SETUP ---
# SCOPES = ["https://google.com"]
# SENDER_EMAIL = "manishnegi.tech@gmail.com"  # Your sender Gmail address

# def get_gmail_credentials():
#     creds = None
#     if os.path.exists(r"gmail_wtsapp\token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(GoogleRequest())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
#             creds = flow.run_local_server(port=0)
#             with open("token.json", "w") as token:
#                 token.write(creds.to_json())
#     return creds


import os
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --- 1. GMAIL OAUTH2 SETUP ---
# FIX: Use the specific Gmail scope required to send emails
# SCOPES = ["https://googleapis.com"]
# SCOPES = ["https://google.com"]
# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]
SENDER_EMAIL = "manishnegi.tech@gmail.com"

# FIX: Keep file paths consistent using a single variable
TOKEN_PATH = os.path.join("gmail_wtsapp", "token.json")
CLIENT_SECRET_PATH = os.path.join("gmail_wtsapp", "client_secret.json")

def get_gmail_credentials():
    creds = None
    
    # 1. Read existing token if it exists
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    # 2. Refresh or authenticate if credentials aren't valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            # FIX: Ensure client_secret.json is looked for in the correct directory
            if not os.path.exists(CLIENT_SECRET_PATH):
                raise FileNotFoundError(f"Please put your downloaded Google credentials file at: {CLIENT_SECRET_PATH}")
                
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # FIX: Ensure the target directory exists before trying to write the token file
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
                
    return creds



creds = get_gmail_credentials()
access_token = creds.token

print(creds, access_token)

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build



import base64
import smtplib

from email.mime.text import MIMEText
from langchain_core.tools import tool



from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64


def write_email(to: str, subject: str, content: str) -> str:
    """Send an email using the Gmail API with OAuth2."""

    try:
        # Get valid OAuth credentials
        creds = get_gmail_credentials()

        # Create Gmail API service
        service = build(
            "gmail",
            "v1",
            credentials=creds
        )

        # Create email
        message = MIMEText(content)

        message["To"] = to
        message["From"] = SENDER_EMAIL
        message["Subject"] = subject

        # Gmail API expects URL-safe base64
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        # Send email
        result = service.users().messages().send(
            userId="me",
            body={
                "raw": raw_message
            }
        ).execute()

        message_id = result.get("id")

        return (
            f"Success! Email has been sent to {to}. "
            f"Message ID: {message_id}"
        )

    except Exception as e:
        return (
            f"Failed to send email to {to}. "
            f"Error: {type(e).__name__}: {str(e)}"
        )

    

# def send_email(creds, to_email, subject, body):

#     # Create Gmail API service
#     service = build("gmail", "v1", credentials=creds)

#     # Create email
#     message = MIMEText(body)

#     message["to"] = to_email
#     message["subject"] = subject

#     # Convert email to Gmail API format
#     raw_message = base64.urlsafe_b64encode(
#         message.as_bytes()
#     ).decode()

#     # Send email
#     result = service.users().messages().send(
#         userId="me",
#         body={"raw": raw_message}
#     ).execute()

#     return result
creds = get_gmail_credentials()

# result = send_email(
#     creds=creds,
#     to_email="manishnegi101@gmail.com",
#     subject="Test Email",
#     body="Hello Manish, this email was sent using the Gmail API."
# )

ans = write_email(to="manishnegi101@gmail.com", subject="Test Email 11", content="Hello Manish, this email was sent using the Gmail API.")
print("Email sent!", ans)
# print("Message ID:", result["id"])