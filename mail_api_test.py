import os
import base64
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from dotenv import load_dotenv

# Google Auth imports
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Twilio and LangGraph imports
from twilio.twiml.messaging_response import MessagingResponse
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model


import os
import base64
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from dotenv import load_dotenv

# Google Auth imports
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Twilio and LangGraph imports
from twilio.twiml.messaging_response import MessagingResponse
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model


SCOPES = ["https://google.com"]
SENDER_EMAIL = "zzz@gmail.com"  # Your sender Gmail address

# 1. FIX: Use the correct email scope

def get_gmail_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds

def write_email(to: str, subject: str, content: str) -> str:
    """Send an actual email using the Google Gmail API via OAuth2."""
    try:
        # Get active Google credentials
        creds = get_gmail_credentials()
        access_token = creds.token

        # Create the email content
        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to

        # 2. FIX: Use the correct smtp address string instead of "://gmail.com"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.ehlo()

        auth_string = f"user={SENDER_EMAIL}\x01auth=Bearer {access_token}\x01\x01"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        server.docmd("AUTH", "XOAUTH2 " + auth_bytes)

        # Send the actual email
        server.send_message(msg)
        server.quit()
        
        return f"Success! The email has been successfully sent to {to}."
    except Exception as e:
        return f"Failed to send email to {to}. Error details: {str(e)}"




if __name__ == "__main__":
    # Example usage
    to = "xyz@gmail.com"
    subject = "Test Email from LangGraph Agent"
    content = "Hello! This email was sent by the LangGraph agent using the Gmail API."
    result = write_email(to, subject, content)  
    print(result)