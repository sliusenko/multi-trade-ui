from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, or_
from app.services.db import SessionLocal, database
from app.models import users
from app.auth.hashing import get_password_hash, verify_password
from app.auth.jwt_handler import create_access_token
from pydantic import BaseModel,  BaseModel, EmailStr

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ❌ Прибираємо локальний префікс, залишаємо тільки tags
router = APIRouter(tags=["Auth"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(users).where(users.c.username == data.username))
    if result.first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(data.password)
    stmt = insert(users).values(username=data.username, email=data.email, password_hash=hashed_password)
    await db.execute(stmt)
    await db.commit()
    return {"status": "registered"}

# @router.post("/login")
# async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(users).where(users.c.username == data.username))
#     db_user = result.first()
#     if not db_user or not verify_password(data.password, db_user._mapping["password_hash"]):
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#
#     token = create_access_token({"sub": str(db_user._mapping["user_id"])})
#     return {"access_token": token, "token_type": "bearer"}

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