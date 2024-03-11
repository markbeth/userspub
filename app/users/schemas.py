from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict


class SAdminAuth(BaseModel):
    is_admin: bool 
    
    model_config = ConfigDict(from_attributes=True)


class SModerAuth(BaseModel):
    is_moder: bool

    model_config = ConfigDict(from_attributes=True)


class SSubAuth(BaseModel):
    is_sub: bool

    model_config = ConfigDict(from_attributes=True)


class SUserSignup(BaseModel):
    email: EmailStr
    password: bytes

    model_config = ConfigDict(from_attributes=True)


class SUserVerify(BaseModel):
    email: str
    verification_code: str
    
    model_config = ConfigDict(from_attributes=True)


class SUserVerifyNewPassword(BaseModel):
    verification_code: str
    password_new: bytes
    
    model_config = ConfigDict(from_attributes=True)

class SUserAuth(BaseModel):
    email: EmailStr
    password: bytes
    
    model_config = ConfigDict(from_attributes=True)

class SUserInfo(BaseModel):
    id: int
    email: EmailStr
    password: bytes
    email: str
    portfolio_id: int
    is_sub: bool 
    is_admin: bool 
    is_moder: bool
    created: date

    model_config = ConfigDict(from_attributes=True)


class SResetEmail(BaseModel):
    verification_code: str
    email_new: str


class SUpdatePortfolioId(BaseModel):
    portfolio_id: int
    email: str