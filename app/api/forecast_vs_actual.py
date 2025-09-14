from datetime import datetime, timedelta
from typing import Optional, Literal

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.services.db import engine  # <- твій async engine

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

VALID_INTERVALS = {
    "1h":  "1 hour",
    "4h":  "4 hours",
    "12h": "12 hours",
    "1d":  "1 day",
    "3d":  "3 days",
}

@router.get("/forecast-vs-actual", response_class=HTMLResponse)
async def forecast_vs_actual_page(request: Request):
    return templates.TemplateResponse("forecast_vs_actual.html", {"request": request})

@router.get("/api/forecast-vs-actual/data")
async def forecast_vs_actual_data(
    exchange: str,
    pair: str,
    timeframe: str,
    interval: str = Query("4h"),
    flh_timeframe: str = Query("5m"),
    user_id: Optional[int] = 0
):
    if interval not in VALID_INTERVALS:
        return {"error": "invalid interval", "allowed": list(VALID_INTERVALS)}

    sql = text("""
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
          AND flh.timeframe  = :flh_timeframe
          AND flh.timestamp BETWEEN NOW() - INTERVAL :interval AND NOW()
        GROUP BY ts_hour
        ORDER BY ts_hour
    """)

    params = {
        "pair": pair.upper(),
        "exchange": exchange.lower(),
        "user_id": user_id,
        "flh_timeframe": flh_timeframe,
        "interval": VALID_INTERVALS[interval],
    }

    assert isinstance(engine, AsyncEngine), "Expected AsyncEngine"
    async with engine.connect() as conn:
        result = await conn.execute(sql, params)
        rows = [dict(x._mapping) for x in result.all()]

    points = [
        {
            "ts": r["ts_hour"].isoformat(),
            "predicted_price": float(r["predicted_price"]) if r["predicted_price"] is not None else None,
            "actual_price": float(r["actual_price"]) if r["actual_price"] is not None else None,
        }
        for r in rows
    ]

    return {
        "exchange": exchange,
        "pair": pair,
        "timeframe": timeframe,
        "interval": interval,
        "flh_timeframe": flh_timeframe,
        "points": points,
    }
