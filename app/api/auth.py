from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from app.services.db import database
from models import users

router = APIRouter()


class RegisterRequest(BaseModel):
    user_id: int
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register_user(data: RegisterRequest):
    # Перевірка, чи існує user_id
    query = select(users).where(users.c.id == data.user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found")

    # Оновлюємо email та пароль
    password_hash = bcrypt.hash(data.password)
    query = users.update().where(users.c.id == data.user_id).values(
        email=data.email, password_hash=password_hash
    )
    await database.execute(query)

    return {"status": "success", "msg": "User registered successfully"}


@router.post("/login")
async def login_user(request: Request, data: LoginRequest):
    query = select(users).where(users.c.email == data.username)
    user = await database.fetch_one(query)

    if not user or not bcrypt.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Зберігаємо сесію
    request.session["user_id"] = user.id

    return {"status": "success", "msg": "Login successful"}


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"status": "success", "msg": "Logged out"})
