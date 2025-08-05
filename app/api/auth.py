from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from app.services.db import database
from app.models import users

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"}
        )

    # Перевірка чи існує користувач
    query = select(users).where(users.c.email == email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )

    # Хешування пароля
    password_hash = bcrypt.hash(password)
    query = users.insert().values(email=email, password_hash=password_hash)
    await database.execute(query)

    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    query = select(users).where(users.c.email == email)
    user = await database.fetch_one(query)

    if not user or not bcrypt.verify(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # Створюємо сесію
    request.session["user_id"] = user.id
    return RedirectResponse(url="/strategy_dashboard", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
