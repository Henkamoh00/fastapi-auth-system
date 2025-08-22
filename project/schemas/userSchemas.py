from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    firstName: str
    lastName: str
    username: str
    gender: bool
    email: EmailStr
    emailIsVerified: bool = False
    birthPlace: Optional[str] = None
    birthDate: Optional[date] = None
    phoneNumber: Optional[str] = None
    locations: Optional[str] = None
    profilePhoto: Optional[str] = None
    isActive: bool = True

    model_config = {
        "from_attributes": True
    }


class UserCreationSchema(UserSchema):
    hashed_password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserUpdateSchema(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[bool] = None
    phoneNumber: Optional[str] = None
    locations: Optional[str] = None
    birthDate: Optional[date] = None
    birthPlace: Optional[str] = None
    profilePhoto: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
    

class PasswordChangingSchema(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

    
    
class VerifyEmailSchema(BaseModel):
    token: str
