from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UserDAO
from app.users.models import User

from fastapi import Depends, Request
from jose import jwt, JWTError
from datetime import datetime, UTC


def get_token(request: Request):
    token  = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try: 
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.now(UTC).timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserDAO.find_by_id(int(user_id))
    if not user: 
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(current_usern: User = Depends(get_current_user)):
    if current_usern.role != "admin":
        raise UserIsNotPresentException 
    return current_usern
    