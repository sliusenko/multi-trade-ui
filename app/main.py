from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api import trades, config, users

app = FastAPI(title="Multi-Trade Bot UI")

# Статика та шаблони
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API маршрути
app.include_router(trades.router, prefix="/api/trades", tags=["Trades"])
app.include_router(config.router, prefix="/api/config", tags=["Config"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
