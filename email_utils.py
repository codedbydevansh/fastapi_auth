import random
import string
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = False, # For Port 587
    MAIL_SSL_TLS = True, # For Port 587
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
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
    await fm.send_message(message)