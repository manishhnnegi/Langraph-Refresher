import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Gmail permission
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


def authenticate_gmail():
    """
    Authenticate Gmail API
    Creates token.json automatically
    """

    creds = None

    # Load token if exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Login if invalid/missing token
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_unread_emails(
    email_address,
    max_results=10
):
    """
    Fetch unread emails
    """

    creds = authenticate_gmail()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    query = (
        f"(to:{email_address} "
        f"OR from:{email_address}) "
        f"is:unread"
    )

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=max_results
        )
        .execute()
    )

    messages = results.get("messages", [])

    if not messages:
        print("No unread emails found.")
        return []

    print(f"\nFound {len(messages)} unread emails:\n")

    email_list = []

    for index, message in enumerate(messages, start=1):

        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"]
            )
            .execute()
        )

        headers = msg["payload"]["headers"]

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

        print("=" * 60)
        print(f"Index      : {index}")
        print(f"Message ID : {msg['id']}")
        print(f"From       : {sender}")
        print(f"Subject    : {subject}")

        email_list.append({
            "index": index,
            "message_id": msg["id"],
            "subject": subject,
            "sender": sender
        })

    return email_list


def mark_as_read(message_id):
    """
    Mark Gmail email as read
    """

    creds = authenticate_gmail()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": ["UNREAD"]
        }
    ).execute()

    print(f"\nEmail marked as READ")
    print(f"Message ID: {message_id}")


if __name__ == "__main__":

    EMAIL = "manishnegi.tech@gmail.com"

    # Step 1: Get unread emails
    emails = get_unread_emails(
        email_address=EMAIL,
        max_results=10
    )

    if emails:

        # Ask user which email to mark read
        choice = int(
            input(
                "\nEnter email index to mark as read: "
            )
        )

        selected_email = next(
            (
                e for e in emails
                if e["index"] == choice
            ),
            None
        )

        if selected_email:

            mark_as_read(
                selected_email["message_id"]
            )

        else:
            print("Invalid selection")