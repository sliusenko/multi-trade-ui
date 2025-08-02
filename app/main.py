from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.api import trades, strategy, signals

app = FastAPI()

# Статика та шаблони
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Авторизація
security = HTTPBasic()
def auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secret":
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return credentials

# API
app.include_router(trades.router, prefix="/api/trades", tags=["Trades"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["Strategy"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])

# Тимчасові дані (імітація БД)
STRATEGY_RULES = [
    {"id": 1, "name": "RSI < 30", "condition": "rsi<30", "enabled": True},
    {"id": 2, "name": "RSI > 70", "condition": "rsi>70", "enabled": False},
]
SIGNAL_LOG = [
    {"pair": "BTCUSDT", "signal": "BUY", "timestamp": "2025-08-02 12:00"},
    {"pair": "ETHUSDT", "signal": "SELL", "timestamp": "2025-08-02 12:05"},
]

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: HTTPBasicCredentials = Depends(auth)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "rules": STRATEGY_RULES
    })

@app.get("/signals", response_class=HTMLResponse)
async def signals_page(request: Request, user: HTTPBasicCredentials = Depends(auth)):
    return templates.TemplateResponse("signals.html", {
        "request": request,
        "signals": SIGNAL_LOG[-50:]
    })
