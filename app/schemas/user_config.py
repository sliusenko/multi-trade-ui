from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str  # 🔐 це потрібно, бо користувач створює пароль

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]
    password: Optional[str]  # 🔐 якщо хоче змінити пароль

class UserOut(UserBase):
    user_id: int

    class Config:
        from_attributes = True  # ✅ для Pydantic v2, замість orm_mode

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str
