from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from app.services.db import engine  # AsyncEngine
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# "як довго дивимось назад" і "як агрегуємо"
VALID_INTERVALS = {
    "1h":  ("1 hour",  "hour"),
    "4h":  ("4 hours", "hour"),
    "12h": ("12 hours","hour"),
    "1d":  ("1 day",   "day"),
    "3d":  ("3 days",  "day"),
}

@router.get("/forecast-vs-actual", response_class=HTMLResponse)
async def forecast_vs_actual_page(request: Request):
    return templates.TemplateResponse("forecast_vs_actual.html", {"request": request})


@router.get("/api/forecast_vs_actual_long")
async def forecast_vs_actual_data(
    request: Request,
    exchange: str,
    pair: str,
    timeframe: str,              # TF для analysis_data (наприклад '1m')
    interval: str,               # 1h/4h/12h/1d/3d
    flh_timeframe: str = "5m",   # TF для FLH (наприклад '5m')
    user_id: Optional[int] = None
):
    lookback, unit = VALID_INTERVALS.get(interval, (None, None))
    if not lookback:
        return {"error": "❌ Невірний інтервал. Доступні: " + ", ".join(VALID_INTERVALS.keys())}

    uid = user_id if user_id is not None else request.session.get("user_id")

    # ⚠️ вставляємо `lookback` напряму (НЕ як параметр)
    sql = text(f"""
        SELECT
            date_trunc(:unit, flh.timestamp)     AS ts,
            AVG(flh.predicted_price)::float      AS predicted_price,
            AVG(ad.price)::float                 AS actual_price
        FROM forecast_longterm_history flh
        JOIN analysis_data ad
          ON  flh.pair      = ad.pair
          AND flh.exchange  = ad.exchange
          AND flh.timeframe = :flh_timeframe
          AND ad.timeframe  = :ad_timeframe
          AND (
                (:uid IS NULL AND flh.user_id IS NULL) OR flh.user_id = :uid
              )
          AND (
                (:uid IS NULL AND ad.user_id  IS NULL) OR ad.user_id  = :uid
              )
          AND date_trunc('minute', ad.timestamp) = date_trunc('minute', flh.timestamp)
        WHERE flh.pair       = :pair
          AND flh.exchange   = :exchange
          AND flh.timestamp >= NOW() - INTERVAL '{lookback}'
        GROUP BY 1
        ORDER BY 1
    """)

    params = {
        "pair": pair,
        "exchange": exchange,
        "uid": uid,
        "ad_timeframe": timeframe,
        "flh_timeframe": flh_timeframe,
        "unit": unit,
        "lookback": lookback,
    }

    async with engine.connect() as conn:
        result = await conn.execute(sql, params)
        rows = [dict(r._mapping) for r in result.fetchall()]

    # твій фронт очікує саме це поле
    return {
        "points": rows,
        "exchange": exchange,
        "pair": pair,
        "timeframe": timeframe,
        "flh_timeframe": flh_timeframe,
        "interval": interval,
        "user_id": uid,
    }
