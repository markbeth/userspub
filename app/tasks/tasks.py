from app.tasks.celery_app import app_celery as app
from app.tasks.email_templates import create_user_confirmation_message
from app.users.models import User
from app.config import settings

import smtplib
import secrets
import string


def create_verification_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))


@app.task
def send_verify_message(
    email: str, verification_code
):
    
    msg_content = create_user_confirmation_message(email, verification_code)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
        