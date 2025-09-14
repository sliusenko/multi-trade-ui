from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.services.db import database
#from app.auth.routes import router as auth_router
from app.auth import router as auth_router
from app.api import config_users
from app.api.strategy import router as strategy_router
from app.api.charts_routes import router as ui_router
from app.api.strategy_sets import router as sets_router
from app.api.strategy_sets_rules import router as strategy_sets_rules
from app.api.strategy_weights import router as weights_router
from app.api.analysis_data import router as analysis_router
from app.api.bot_activity_routes import router as bot_activity_router
from app.api.forecast_vs_actual import router as forecast_vs_actual_router

app = FastAPI()

# === Папки та шаблони ===
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# === Роутери ===
app.include_router(auth_router, prefix="/api/auth")
app.include_router(strategy_router)
app.include_router(config_users.router)
app.include_router(sets_router)
app.include_router(strategy_sets_rules)
app.include_router(weights_router)
app.include_router(ui_router)
app.include_router(analysis_router)
app.include_router(bot_activity_router)
app.include_router(forecast_vs_actual_router)
app.router.redirect_slashes = False

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
    return FileResponse("login.html")

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
    rows = await database.fetch_all(query)  # якщо це databases, ок; якщо SA Row -> дивись нижче
    return [StrategyRuleResponse.model_validate(r) for r in rows]

@app.get("/config_users")
def config_users_page(request: Request):
    return templates.TemplateResponse("config_users.html", {"request": request})
