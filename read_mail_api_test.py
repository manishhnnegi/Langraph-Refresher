import os
import base64
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Gmail permissions
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


def authenticate_gmail():
    """
    Authenticate Gmail API
    Creates token.json automatically
    """

    creds = None

    # Load saved token if exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Login if token missing/expired
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def extract_email_body(payload):
    """
    Extract email body text
    """

    if "parts" in payload:

        for part in payload["parts"]:

            mime_type = part.get("mimeType")

            if mime_type == "text/plain":
                data = part["body"].get("data")

                if data:
                    return base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8")

    data = payload.get("body", {}).get("data")

    if data:
        return base64.urlsafe_b64decode(
            data
        ).decode("utf-8")

    return "No body found"


def fetch_emails(
    email_address,
    minutes_since=60,
    unread_only=True
):
    """
    Fetch emails from Gmail
    """

    creds = authenticate_gmail()
    all_emails = []
    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    # Time filter
    after_timestamp = int(
        (
            datetime.now() -
            timedelta(minutes=minutes_since)
        ).timestamp()
    )

    # Gmail query
    query = (
        f"(to:{email_address} "
        f"OR from:{email_address}) "
        f"after:{after_timestamp}"
    )

    if unread_only:
        query += " is:unread"

    print("\nSearching Query:")
    print(query)

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query
        )
        .execute()
    )

    messages = results.get("messages", [])

    if not messages:
        print("\nNo emails found.")
        return

    print(f"\nFound {len(messages)} emails\n")

    for idx, message in enumerate(messages, start=1):

        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"]
            )
            .execute()
        )

        payload = msg["payload"]
        headers = payload["headers"]

        subject = next(
            (
                h["value"]
                for h in headers
                if h["name"] == "Subject"
            ),
            "No Subject"
        )

        sender = next(
            (
                h["value"]
                for h in headers
                if h["name"] == "From"
            ),
            "Unknown Sender"
        )

        to_email = next(
            (
                h["value"]
                for h in headers
                if h["name"] == "To"
            ),
            "Unknown"
        )

        date = next(
            (
                h["value"]
                for h in headers
                if h["name"] == "Date"
            ),
            "Unknown"
        )

        body = extract_email_body(payload)

        print("=" * 70)
        print(f"Email #{idx}")
        print("=" * 70)

        print("Message ID:", msg["id"])
        print("Thread ID :", msg["threadId"])
        print("From      :", sender)
        print("To        :", to_email)
        print("Subject   :", subject)
        print("Date      :", date)

        print("\nBody:")
        print(body[:500])

        print("\n")

        # STORE FOR RETURN
        email_data = {
            "email_number": idx,
            "message_id": msg["id"],
            "thread_id": msg["threadId"],
            "from": sender,
            "to": to_email,
            "subject": subject,
            "date": date,
            "body": body[:500]
        }

        all_emails.append(email_data)

    return  all_emails


if __name__ == "__main__":

    all_emails = fetch_emails(
        email_address="manishnegi.tech@gmail.com",
        minutes_since=1440,   # last 24 hours
        unread_only=False
    )

    print(all_emails[:4])
    print(len(all_emails), "emails fetched in total")