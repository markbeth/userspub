from app.config import settings
from email.message import EmailMessage
from pydantic import EmailStr


def create_user_confirmation_message(
    email_to: EmailStr,
    verification_code
):
    email = EmailMessage()
    email["Subject"] = "Verfification message"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    
    email.set_content(
        f"""
        <h1>Confirm by using code below on verification page: </h1>
        {verification_code}
        """,
        subtype="html"
    )
    return email