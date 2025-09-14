from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from app.services.db import engine  # твій AsyncEngine
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

VALID_INTERVALS = {
    "1h": "1 hour",
    "4h": "4 hours",
    "12h": "12 hours",
    "1d": "1 day",
    "3d": "3 days"
}

@router.get("/forecast-vs-actual", response_class=HTMLResponse)
async def forecast_vs_actual_page(request: Request):
    return templates.TemplateResponse("forecast_vs_actual.html", {"request": request})


@router.get("/api/forecast_vs_actual_long")
async def forecast_vs_actual_data(
    request: Request,
    exchange: str,
    pair: str,
    timeframe: str,
    interval: str,
    flh_timeframe: str = "5m",
    user_id: Optional[int] = None
):
    interval_sql = VALID_INTERVALS.get(interval)
    if not interval_sql:
        return {"error": "❌ Невірний інтервал. Доступні: " + ", ".join(VALID_INTERVALS)}

    sql = text(f"""
        SELECT
            date_trunc('hour', flh.timestamp)      AS ts_hour,
            AVG(flh.predicted_price)               AS predicted_price,
            AVG(ad.price)                          AS actual_price
        FROM forecast_longterm_history flh
        JOIN analysis_data ad
          ON  flh.pair      = ad.pair
          AND flh.exchange  = ad.exchange
          AND flh.user_id   = ad.user_id
          AND flh.timeframe = ad.timeframe
          AND date_trunc('minute', flh.timestamp) = date_trunc('minute', ad.timestamp)
        WHERE flh.pair       = :pair
          AND flh.exchange   = :exchange
          AND flh.user_id    = :user_id
          AND flh.timeframe  = :timeframe
          AND flh.timestamp BETWEEN NOW() - INTERVAL '{interval_sql}' AND NOW()
        GROUP BY ts_hour
        ORDER BY ts_hour
    """)

    params = {
        "pair": pair,
        "exchange": exchange,
        "user_id": user_id or request.session.get("user_id") or 0,
        "timeframe": flh_timeframe,
    }

    async with engine.connect() as conn:
        result = await conn.execute(sql, params)
        rows = [dict(r._mapping) for r in result.fetchall()]

    return {"rows": rows}
