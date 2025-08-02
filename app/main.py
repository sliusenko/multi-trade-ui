from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import bcrypt
import psycopg2
from sqlalchemy import select
from app.services.db import database
from app.api import strategy
from app.models import strategy_rules, strategy_conditions, strategy_sets, strategy_weights
from pydantic import BaseModel


# Ініціалізація FastAPI
app = FastAPI()
app.include_router(strategy.router, prefix="/api")
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

templates = Jinja2Templates(directory="app/templates")

# ====== Авторизація ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    user_id: int
    email: str
    password: str


@app.post("/register")
def register_user(data: RegisterRequest):
    conn = psycopg2.connect("dbname=tradebot user=postgres password=postgres host=localhost")
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id=%s", (data.user_id,))
    result = cur.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="User ID not found")

    password_hash = bcrypt.hash(data.password)
    cur.execute("""
        UPDATE users
        SET email=%s, password_hash=%s
        WHERE user_id=%s
    """, (data.email, password_hash, data.user_id))

    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "msg": "User registered successfully"}

def get_db():
    return psycopg2.connect(
        host="172.19.0.1",
        database="tradebot",
        user="bot",
        password="00151763Db3c"
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

def require_login(request: Request):
    return bool(request.session.get("user"))

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, password_hash FROM users WHERE email=%s", (username,))
    row = cur.fetchone()
    conn.close()

    # Для тесту приймаємо і звичайний пароль, і bcrypt
    if row and (row[1] == password or bcrypt.verify(password, row[1])):
        request.session["user"] = str(row[0])
        return RedirectResponse(url="/strategy_dashboard", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"}
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ====== Strategy Dashboard ======

@app.get("/strategy_dashboard", response_class=HTMLResponse)
async def strategy_dashboard(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

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


# ====== Підключення до БД ======

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
