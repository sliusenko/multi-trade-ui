from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, MetaData, select
from databases import Database

# =====================
# Database config
# =====================
DATABASE_URL = "postgresql://user:password@<VM-IP>:5432/tradebot"  # заміни на свій

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

# =====================
# FastAPI app
# =====================
app = FastAPI()

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Session middleware
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")


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
