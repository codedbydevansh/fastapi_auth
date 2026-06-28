import random
import string
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv(MAIL_USERNAME),
    MAIL_PASSWORD = os.getenv(MAIL_PASSWORD),
    MAIL_FROM = os.getenv(MAIL_FROM),
    MAIL_PORT = 465,              # Port 465 is more stable on Railway
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,        # False for 465
    MAIL_SSL_TLS = True,          # True for 465
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False,       # This prevents handshake delays on cloud servers
    TIMEOUT = 60
)

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: str, code: str):
    message = MessageSchema(
        subject="TaskMaster Pro - Verify Your Email",
        recipients=[email],
        body=f"Your verification code is: {code}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    # We use await here to ensure the connection is established before moving on
    await fm.send_message(message)