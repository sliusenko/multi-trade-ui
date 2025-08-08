from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str
