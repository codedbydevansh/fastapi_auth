# schemas.py

from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TodoBase(BaseModel):
    title: str
    is_completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoResponse(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class VerifyEmail(BaseModel):
    email: EmailStr
    code: str

class OTPRequest(BaseModel):
    email: EmailStr

class RegisterWithOTP(BaseModel):
    username: str
    email: EmailStr
    password: str
    otp_code: str