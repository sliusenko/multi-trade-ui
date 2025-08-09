from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.services.db import database
from app.api.strategy import router as strategy_router
#from app.auth.routes import router as auth_router
from app.auth import router as auth_router
from app.api import config_users
from app.api.strategy_sets import router as sets_router
from app.api.strategy_set_rules import router as set_rules_router
from app.api.strategy_weights import router as weights_router

app = FastAPI()

# === Папки та шаблони ===
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# === Роутери ===
app.include_router(auth_router, prefix="/api/auth")
app.include_router(strategy_router)
app.include_router(config_users.router)
app.include_router(sets_router)
app.include_router(set_rules_router)
app.include_router(weights_router)

# === Middleware для сесій ===
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# === Статичні файли (доступні по /static/...) ===
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# === Тимчасові тестові правила ===
rules = [
    {"id": 1, "action": "Buy", "condition_type": "RSI<30", "enabled": True},
    {"id": 2, "action": "Sell", "condition_type": "RSI>70", "enabled": False},
]

templates = Jinja2Templates(directory="app/templates")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# === Події старта та завершення ===
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# === Роут для головної сторінки ===
@app.get("/")
async def home():
    # Віддаємо login.html як стартову сторінку
    return FileResponse("app/static/login.html")

# === Дашборд стратегії ===
@app.get("/strategy_dashboard")
async def strategy_dashboard(request: Request):
    return templates.TemplateResponse("strategy_dashboard.html", {
        "request": request,
        "rules": rules
    })

@app.get("/api/strategy_rules")
async def get_rules():
    return rules

@app.get("/config_users")
def config_users_page(request: Request):
    return templates.TemplateResponse("config_users.html", {"request": request})
