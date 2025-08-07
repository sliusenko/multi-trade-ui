from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, or_
from app.services.db import database
from app.models import users
from app.auth.jwt_handler import create_access_token

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
    query = select(users).where(users.c.user_id == data.user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found")

    # Оновлюємо email та пароль
    password_hash = bcrypt.hash(data.password)
    query = users.update().where(users.c.user_id == data.user_id).values(
        email=data.email, password_hash=password_hash
    )
    await database.execute(query)

    return {"status": "success", "msg": "User registered successfully"}


@router.post("/login")
async def login_user(request: Request, data: LoginRequest):
    query = select(users).where(
        or_(
            users.c.username == data.username,
            users.c.email == data.username
        )
    )
    user = await database.fetch_one(query)

    if not user or not bcrypt.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user["user_id"])
    return {"access_token": token}

# @router.post("/login")
# async def login_user(request: Request, data: LoginRequest):
#     query = select(users).where(
#         (users.c.username == data.username) | (users.c.email == data.username)
#     )
#     user = await database.fetch_one(query)
#
#     if not user or not bcrypt.verify(data.password, user["password_hash"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     request.session["user_id"] = user["user_id"]
#
#     return {"access_token": create_access_token(user["user_id"])}


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"status": "success", "msg": "Logged out"})
