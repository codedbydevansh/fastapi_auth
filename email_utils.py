import random
import string
import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Helper function to safely get variables without quotes or spaces
def get_safe_env(key: str, default: str = "") -> str:
    value = os.getenv(key, default)
    if value:
        # Removes both double quotes, single quotes, and extra spaces
        return value.strip().replace('"', '').replace("'", "")
    return default

mail_user = get_safe_env("MAIL_USERNAME")
mail_pass = SecretStr(get_safe_env("MAIL_PASSWORD"))
mail_from = get_safe_env("MAIL_FROM")
mail_server = get_safe_env("MAIL_SERVER", "smtp.gmail.com")

# Safely convert port to integer
try:
    mail_port = int(get_safe_env("MAIL_PORT", "587"))
except ValueError:
    mail_port = 587

conf = ConnectionConfig(
    MAIL_USERNAME = mail_user,
    MAIL_PASSWORD = mail_pass,
    MAIL_FROM = mail_from,
    MAIL_PORT = mail_port,
    MAIL_SERVER = mail_server,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
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