from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import bcrypt
import psycopg2
from sqlalchemy import select
from app.services.db import database
from app.api import strategy
from app.models import strategy_rules, strategy_conditions, strategy_sets, strategy_weights

# Ініціалізація FastAPI
app = FastAPI()
app.include_router(strategy.router, prefix="/api")
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

templates = Jinja2Templates(directory="app/templates")

# ====== Авторизація ======

def get_db():
    return psycopg2.connect(
        host="172.19.0.1",
        database="tradebot",
        user="bot",
        password="00151763Db3c"
    )

def require_login(request: Request):
    return bool(request.session.get("user"))

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_action(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, password_hash FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    conn.close()

    if row and bcrypt.verify(password, row[1]):
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
