from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.strategy import router as strategy_router
from pathlib import Path

app = FastAPI()
app.include_router(strategy_router)
# Секретний ключ для сесій
app.add_middleware(SessionMiddleware, secret_key="supersecret")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Тимчасова база правил
rules = [
    {"id": 1, "action": "Buy", "condition_type": "RSI<30", "enabled": True},
    {"id": 2, "action": "Sell", "condition_type": "RSI>70", "enabled": False},
]

@app.get("/")
async def home():
    return RedirectResponse("/strategy_dashboard")

@app.get("/strategy_dashboard")
async def strategy_dashboard(request: Request):
    return templates.TemplateResponse("strategy_dashboard.html", {
        "request": request,
        "rules": rules
    })

# === API endpoints for JS fetch() ===

@app.post("/api/strategy_rules")
async def add_rule(rule: dict):
    new_id = max(r["id"] for r in rules) + 1 if rules else 1
    rule["id"] = new_id
    rules.append(rule)
    return rule

@app.delete("/api/strategy_rules/{rule_id}")
async def delete_rule(rule_id: int):
    global rules
    rules = [r for r in rules if r["id"] != rule_id]
    return {"status": "deleted"}

@app.put("/api/strategy_rules/{rule_id}")
async def update_rule(rule_id: int, rule: dict):
    for r in rules:
        if r["id"] == rule_id:
            r.update(rule)
            return r
    return {"error": "not found"}


