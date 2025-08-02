from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Session middleware (SECRET_KEY треба змінити)
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

# ===== Login =====
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    # Простий логін (можна зробити з БД)
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
    if not request.session.get("user"):
        return False
    return True

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login")
    # Тут підставиш свої strategy_rules
    rules = [
        {"id": 1, "name": "RSI Buy < 30"},
        {"id": 2, "name": "MACD Cross"},
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "rules": rules})

@app.get("/signals", response_class=HTMLResponse)
async def signals(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login")
    # Тут підставиш лог із record_signal
    signals = [
        {"time": "2025-08-02 12:00", "pair": "BTCUSDT", "signal": "BUY"},
        {"time": "2025-08-02 12:05", "pair": "ETHUSDT", "signal": "SELL"},
    ]
    return templates.TemplateResponse("signals.html", {"request": request, "signals": signals})
