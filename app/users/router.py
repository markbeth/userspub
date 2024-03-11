from app.exceptions import IncorrectEmailOrPasswordException, InvalidVerificationCode, UserAlreadyExistsException, UserIsNotPresentException
from app.tasks.tasks import create_verification_code, send_verify_message
from app.users.dao import UserDAO
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import User
from app.users.schemas import SUpdatePortfolioId, SUserAuth, SAdminAuth, SModerAuth, SUserInfo, SSubAuth, SResetEmail, SUserSignup, SUserVerify, SUserVerifyNewPassword
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.logger import logger

from datetime import datetime, UTC
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_versioning import version
from dateutil.tz import tzutc


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/signup")
@version(1)
async def signup_user(user_data: SUserSignup):
    try:
        existing_user = await UserDAO.find_one_or_none(email=user_data.email)

        if existing_user:
            msg = "User already exists"
            logger.error(msg, extra={"email": existing_user.email}, exc_info=True)
            raise UserAlreadyExistsException
        
        password_hashed = get_password_hash(user_data.password)
        verification_code = create_verification_code()
        user = await UserDAO.add_return_obj(email=user_data.email, password_hashed=password_hashed, verification_code=verification_code)
        # user_dict = SUserInfo.model_validate(user).model_dump()
        send_verify_message.delay(user.email, verification_code)
        # return RedirectResponse(url="/v1/auth/verify_email")
        item = {
            "email": user_data.email,
            "message": "User created successfully. Verification code sent to email.",
            "time": datetime.now(tz=tzutc()).isoformat()
            }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

    except Exception as e:
        msg = "Unknown Exc: Cannot signup new user"
        logger.error(msg, extra=user_data.model_dump(), exc_info=True)
        # raise e


@router.post("/verify_email")
@version(1)
async def verify_email(user_data: SUserVerify):
    try:
        current_user = await UserDAO.find_obj(email=user_data.email)
        if not current_user:
            msg = "User don't exists"
            logger.error(msg, extra={"email": user_data.email}, exc_info=True)
            raise UserIsNotPresentException
        
        item = {
            "email": user_data.email,
            "message": "",
            "time": datetime.now(tz=tzutc()).isoformat()
            }
        if user_data.verification_code != current_user.verification_code:
            item["message"] = "Invalid verification code"
            return JSONResponse(status_code=status.HTTP_417_EXPECTATION_FAILED, content=item)
        
        await UserDAO.update_verification_status(current_user.email)
        # return RedirectResponse(url="/login")
        item["message"] = "Email successfully verified"
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=item)
        
    except Exception as e:
        msg = "Unknown Exc: Cannot verify email of new user"
        logger.error(msg, extra=user_data.model_dump(), exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)
    


@router.post("/login")
@version(1)
async def login_user(response: Response, user_data: SUserAuth):
    try:
        user = await authenticate_user(user_data.email, user_data.password)

        if not user:
            msg = "User don't exists"
            logger.error(msg, extra={"email": user_data.email}, exc_info=True)
            raise IncorrectEmailOrPasswordException
        
        item = {
            "email": user_data.email,
            "message": "",
            "time": datetime.now(tz=tzutc()).isoformat()
            }
        
        if not user.is_verified:
            item["message"] = "Email not verified"
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=item)
        
        access_token = create_access_token({"sub": str(user.id)})
        response.set_cookie("access_token", access_token, httponly=True)
        return {"access_token": access_token}
    
    except Exception as e:
        msg = "Unknown Exc: Cannot login user"
        logger.error(msg, extra=user_data.model_dump(), exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)


@router.post("/logout")
@version(1)
async def logout_user(response: Response):
    try:
        response.delete_cookie("access_token", httponly=True)
        item = {
            "mesage": "Successfully logout",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=item)
    
    except Exception as e:
        msg = "Unknown Exc: Cannot logout user"
        logger.error(msg, extra=response, exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)


@router.post("/delete_user")
@version(1)
async def delete_user(response: Response, current_user: User = Depends(get_current_user)):
    try:
        item = {
            "email": current_user.email,
            "message": "User deleted",
            "time": datetime.now(tz=tzutc()).isoformat()
            }
        await UserDAO.delete(id=current_user.id)
        response.delete_cookie("access_token", httponly=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=item)
    
    except Exception as e:
        msg = "Unknown Exc: Cannot delete user"
        logger.error(msg, extra=current_user, exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)
    

@router.get("/me")
@version(1)
async def read_users_me(current_user: User = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        msg = "Unknown Exc: Cannot read current user"
        logger.error(msg, extra=current_user, exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)


@router.get("/all")
@version(1)
async def read_users_all(current_user: User = Depends(get_current_admin_user)):
    try:
        if current_user.is_admin:
            return await UserDAO.find_all()
        item = {
            "email": current_user.email,
            "mesage": "Unauthorized",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=item)

    except Exception as e:
        msg = "Unknown Exc: Cannot read all users"
        logger.error(msg, extra=current_user, exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)


@router.post("/verify_password")
@version(1)
async def verify_password(user_data: SUserVerifyNewPassword, current_user: User = Depends(get_current_user)):
    try:
        # user = await UserDAO.find_obj(email=user_data.email)
        
        if user_data.verification_code != current_user.verification_code:
            msg = "Code missmatch"
            logger.error(msg, extra=current_user, exc_info=True)
            raise InvalidVerificationCode
        
        password_hashed = get_password_hash(user_data.password_new)
        user = await UserDAO.update(filter_by={"email":current_user.email}, password_hashed=password_hashed)
        # return RedirectResponse(url="/login")
        item = {
            "email": current_user.email,
            "mesage": "Password successfully verified",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=item)
        
    except Exception as e:
        msg = "Unknown Exc: Cannot verify new password"
        logger.error(msg, extra=user_data.model_dump(), exc_info=True)
        item = {
            "mesage": msg,
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=item)


@router.post("/reset_password")
@version(1)
async def reset_password(current_user: User = Depends(get_current_user)):
    # user = await authenticate_user(user_data.email, user_data.password_old)
    try:
        
        verification_code = create_verification_code()
        await UserDAO.update(filter_by={"email":current_user.email}, verification_code=verification_code)    
        send_verify_message.delay(current_user.email, verification_code)
        
        # return RedirectResponse(url="/verify_password")
        item = {
            "email": current_user.email,
            "mesage": f"Reset code sent to email: {current_user.email}",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=item)
    
    except IncorrectEmailOrPasswordException:
        msg = "IncorrectEmailOrPasswordException"
        logger.error(msg, extra={"email": current_user.email}, exc_info=True)
        raise IncorrectEmailOrPasswordException
    

@router.post("/verify_new_email")
@version(1)
async def verify_new_email(user_data: SResetEmail, current_user: User = Depends(get_current_user)):

    if user_data.verification_code != current_user.verification_code:
        msg = "Code missmatch"
        logger.error(msg, extra=current_user, exc_info=True)
        raise InvalidVerificationCode

        
    user = await UserDAO.update(filter_by={"email":current_user.email}, email=user_data.email_new)
    await UserDAO.downgrade_verification_status(current_user.email)
    # return RedirectResponse(url="/login")
    item = {
            "email": current_user.email,
            "mesage": f"Success, verify new email, code sent to {user_data.email_new}",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
    return JSONResponse(status_code=status.HTTP_200_OK, content=item)
    

@router.post("/reset_email")
@version(1)
async def reset_email(current_user: User = Depends(get_current_user)):
    verification_code = create_verification_code()
    
    await UserDAO.update(filter_by={"email":current_user.email}, verification_code=verification_code) 
    await UserDAO.downgrade_verification_status(current_user.email)   
    send_verify_message.delay(current_user.email, verification_code)
    
    # return RedirectResponse(url="/verify_new_email")
    item = {
            "email": current_user.email,
            "mesage": f"Success, verify new email, code sent to {current_user.email}",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
    return JSONResponse(status_code=status.HTTP_200_OK, content=item)


@router.post("/update_portfolio_id")
@version(1)
async def update_portfolio_id(user_data: SUpdatePortfolioId):
    user = await UserDAO.find_obj(email=user_data.email)
    if not user:
        msg = "UserIsNotPresentException"
        logger.error(msg, extra=user_data.model_dump(), exc_info=True)
        return UserIsNotPresentException
    
    await UserDAO.update(filter_by={"email":user_data.email}, portfolio_id=user_data.portfolio_id) 
    item = {
            "email": user_data.email,
            "mesage": f"User portfilio id updated",
            "time": datetime.now(tz=tzutc()).isoformat()
        }
    return JSONResponse(status_code=status.HTTP_200_OK, content=item)
