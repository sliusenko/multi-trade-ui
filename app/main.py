from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Depends, HTTPException
from passlib.hash import bcrypt
import psycopg2
from app.services.db import database
from app.api import strategy
from sqlalchemy import select
from app.models import strategy_rules, strategy_conditions, strategy_sets, strategy_weights

app = FastAPI()

# Підключаємо API-роути
app.include_router(strategy.router, prefix="/api")

# Підключаємо сесії
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

# Шаблони
templates = Jinja2Templates(directory="app/templates")


# ====== Авторизація ======

def require_login(request: Request):
    """Перевірка, чи користувач залогінений"""
    return bool(request.session.get("user"))

app = FastAPI()

def verify_user(email, password):
    conn = psycopg2.connect("dbname=tradebot user=admin")
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    if row and bcrypt.verify(password, row[0]):
        return True
    return False

@app.post("/login")
def login(email: str, password: str):
    if verify_user(email, password):
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    # Простий приклад логіну
    if username == "admin" and password == "admin123":
        request.session["user"] = username
        return RedirectResponse(url="/strategy_dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ====== Strategy Dashboard ======

@app.get("/strategy_dashboard", response_class=HTMLResponse)
async def strategy_dashboard(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    try:
        # Отримуємо дані з БД
        rules = await database.fetch_all(select(strategy_rules).order_by(strategy_rules.c.id))
        conditions = await database.fetch_all(select(strategy_conditions).order_by(strategy_conditions.c.id))
        sets_ = await database.fetch_all(select(strategy_sets).order_by(strategy_sets.c.id))
        weights = await database.fetch_all(select(strategy_weights).order_by(
            strategy_weights.c.user_id,
            strategy_weights.c.exchange,
            strategy_weights.c.pair
        ))

        def to_dict_list(records):
            return [dict(r) for r in records] if records else []

        return templates.TemplateResponse(
            "strategy_dashboard.html",
            {
                "request": request,
                "rules": to_dict_list(rules),
                "conditions": to_dict_list(conditions),
                "sets": to_dict_list(sets_),
                "weights": to_dict_list(weights),
            }
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>Internal Server Error</h1><pre>{e}</pre>", status_code=500)


# ====== Старт/Стоп БД ======

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

