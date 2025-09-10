from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# якщо у тебе вже є templates у dependencies.py — імпортуй його
templates = Jinja2Templates(directory="app/templates")

@router.get("/indicators", response_class=HTMLResponse)
async def indicators_page(request: Request):
    return templates.TemplateResponse("indicators.html", {"request": request})
