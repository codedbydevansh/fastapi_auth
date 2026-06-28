import random
import string
import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Provide defaults to avoid NoneType errors
mail_user = os.getenv("MAIL_USERNAME", "")
mail_pass = SecretStr(os.getenv("MAIL_PASSWORD", ""))
mail_from = os.getenv("MAIL_FROM", "")

conf = ConnectionConfig(
    MAIL_USERNAME = mail_user,
    MAIL_PASSWORD = mail_pass,
    MAIL_FROM = mail_from,
    MAIL_PORT = 587,                   # Changed to 587 for Railway stability
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,              # True for 587
    MAIL_SSL_TLS = False,              # False for 587
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False,
    TIMEOUT = 60
)

def generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: str, code: str):
    message = MessageSchema(
        subject="TaskMaster Pro - Verify Your Email",
        recipients=[email],  # type: ignore 
        body=f"Your verification code is: {code}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)