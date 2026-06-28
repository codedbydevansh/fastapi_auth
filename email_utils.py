import random
import string
import os
from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
from pydantic import SecretStr, EmailStr  # Import EmailStr

load_dotenv()

# Extract and cast variables
mail_user = os.getenv("MAIL_USERNAME", "")
mail_pass = SecretStr(os.getenv("MAIL_PASSWORD", ""))
mail_from = os.getenv("MAIL_FROM", "")
mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
mail_port = int(os.getenv("MAIL_PORT", "465"))

conf = ConnectionConfig(
    MAIL_USERNAME = mail_user,
    MAIL_PASSWORD = mail_pass,
    MAIL_FROM = mail_from,
    MAIL_PORT = mail_port,
    MAIL_SERVER = mail_server,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False,
    TIMEOUT = 60
)

def generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: str, code: str):
    # We explicitly cast the recipient to EmailStr to satisfy the type checker
    recipient_list: List[EmailStr] = [EmailStr(email)]
    
    message = MessageSchema(
        subject="TaskMaster Pro - Verify Your Email",
        recipients=recipient_list, # Pylance is now happy with List[EmailStr]
        body=f"Your verification code is: {code}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)