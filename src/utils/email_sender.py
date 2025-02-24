import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import msal
import json

# Load OAuth2 credentials
CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "credentials", "oauth2_credentials.json"
)


def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as file:
            credentials = json.load(file)
            return credentials
    return None


def save_credentials(credentials):
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as file:
        json.dump(credentials, file)


def get_access_token():
    credentials = load_credentials()
    if not credentials:
        return None

    CLIENT_ID = credentials["client_id"]
    TENANT_ID = credentials["tenant_id"]
    CLIENT_SECRET = credentials["client_secret"]
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://outlook.office365.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_silent(SCOPES, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPES)
    return result["access_token"]


def send_email(file_paths, recipient_email, sender_email):
    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg["Subject"] = f"New Files Detected at {timestamp}"

    # Attach files to the email
    for file_path in file_paths:
        if os.path.isfile(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(file_path)}",
                )
                msg.attach(part)

    # Set up the SMTP server and send the email using OAuth2
    try:
        access_token = get_access_token()
        if not access_token:
            raise Exception("OAuth2 credentials not found or invalid.")
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.docmd("AUTH", "XOAUTH2 " + access_token)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
