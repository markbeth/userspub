import bcrypt
from datetime import UTC, datetime, timedelta
from jose import jwt
from pydantic import EmailStr

from app.users.dao import UserDAO
from app.config import settings


def get_password_hash(password:str) -> bytes:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password, salt=salt)
    return hashed_password


def verify_password(plain_password, hashed_password) -> bool:
    if isinstance(plain_password, str):
        password_byte_enc = plain_password.encode('utf-8')
    else:
        password_byte_enc = plain_password
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        # to_encode, "secret1", "HS256"
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    user = await UserDAO.find_one_or_none(email=email)
    if user and verify_password(password, user.password_hashed) and user.is_verified:
        return user