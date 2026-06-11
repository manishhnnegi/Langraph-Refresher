import os
import base64
import smtplib
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://mail.google.com/"]
SENDER_EMAIL = "manishnegi.tech@gmail.com"


def get_gmail_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

    return creds


def write_email(to, subject, content):

    try:
        creds = get_gmail_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        access_token = creds.token

        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to

        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.ehlo()
        server.starttls()
        server.ehlo()

        auth_string = (
            f"user={SENDER_EMAIL}\x01"
            f"auth=Bearer {access_token}\x01\x01"
        )

        auth_bytes = base64.b64encode(
            auth_string.encode("utf-8")
        ).decode("utf-8")

        response = server.docmd(
            "AUTH",
            "XOAUTH2 " + auth_bytes
        )

        print("AUTH RESPONSE:", response)

        server.send_message(msg)
        server.quit()

        return f"Email sent to {to}"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":

    # IMPORTANT:
    # Delete token.json before first run
    result = write_email(
        "manishnegiai@gmail.com",
        "Hello from Gmail MTP!",
        "Hello from Gmail MTP!"
    )

    print(result)