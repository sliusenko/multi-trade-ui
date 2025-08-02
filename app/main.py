from fastapi import FastAPI, Request, Form
from fastapi.encoders import jsonable_encoder
import json
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, MetaData, select
from databases import Database

# =====================
# Database config
# =====================
DATABASE_URL = "postgresql://bot:00151763Db3c@172.17.0.1:5432/tradebot"  # заміни на свій

database = Database(DATABASE_URL)
metadata = MetaData()

strategy_rules = Table(
    "strategy_rules", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("exchange", String),
    Column("pair", String),
    Column("action", String),
    Column("condition_type", String),
    Column("param_1", Float),
    Column("param_2", Float),
    Column("enabled", Boolean),
    Column("priority", Integer),
)

strategy_conditions = Table(
    "strategy_conditions", metadata,
    Column("id", Integer, primary_key=True),
    Column("rule_id", Integer),
    Column("param_name", String),
    Column("param_value", Float),
)

strategy_sets = Table(
    "strategy_sets", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("name", String),
)

strategy_weights = Table(
    "strategy_weights", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("exchange", String, primary_key=True),
    Column("pair", String, primary_key=True),
    Column("rsi_weight", Float),
    Column("forecast_weight", Float),
    Column("acceleration_weight", Float),
    Column("trade_logic", String),
)
# =====================
# FastAPI app
# =====================
app = FastAPI()

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Session middleware
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

@app.get("/strategy_dashboard", response_class=HTMLResponse)
async def strategy_dashboard(request: Request):
    # Якщо не залогінений – редірект на логін
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    try:
        # Асинхронно тягнемо всі таблиці (порожні теж повернуть [])
        rules = await database.fetch_all(select(strategy_rules).order_by(strategy_rules.c.id))
        conditions = await database.fetch_all(select(strategy_conditions).order_by(strategy_conditions.c.id))
        sets_ = await database.fetch_all(select(strategy_sets).order_by(strategy_sets.c.id))
        weights = await database.fetch_all(
            select(strategy_weights).order_by(
                strategy_weights.c.user_id,
                strategy_weights.c.exchange,
                strategy_weights.c.pair
            )
        )

        # Перетворюємо записи в списки словників
        def to_dict_list(records):
            return [dict(r) for r in records] if records else []

        data_json = {
            "rules": to_dict_list(rules),
            "conditions": to_dict_list(conditions),
            "sets": to_dict_list(sets_),
            "weights": to_dict_list(weights),
        }

        # Передаємо готовий JSON у шаблон
        return templates.TemplateResponse(
            "strategy_dashboard.html",
            {
                "request": request,
                "data_json": json.dumps(data_json, default=str),  # default=str для безпечного JSON
            }
        )

    except Exception as e:
        # Лог для діагностики
        print(f"[ERROR] strategy_dashboard: {e}")
        # Можна зробити кастомну сторінку 500
        return HTMLResponse(content=f"<h1>Internal Server Error</h1><pre>{e}</pre>", status_code=500)

# Startup / Shutdown
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# ===== Login =====
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    # Простий логін
    if username == "admin" and password == "admin123":
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ===== Protected Routes =====
def require_login(request: Request):
    return bool(request.session.get("user"))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login")

    query = select(strategy_rules).order_by(strategy_rules.c.id)
    rules = await database.fetch_all(query)

    # Перетворимо на список словників для шаблону
    rules_list = [
        {
            "id": r.id,
            "name": f"{r.action} ({r.condition_type})",
            "condition": r.condition_type,
            "enabled": r.enabled,
        }
        for r in rules
    ]

    return templates.TemplateResponse("dashboard.html", {"request": request, "rules": rules_list})


@app.get("/signals", response_class=HTMLResponse)
async def signals(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login")

    # TODO: Підключити реальні сигнали з таблиці
    signals = [
        {"time": "2025-08-02 12:00", "pair": "BTCUSDT", "signal": "BUY"},
        {"time": "2025-08-02 12:05", "pair": "ETHUSDT", "signal": "SELL"},
    ]
    return templates.TemplateResponse("signals.html", {"request": request, "signals": signals})
