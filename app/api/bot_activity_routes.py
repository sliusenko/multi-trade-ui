# app/api/bot_activity_routes.py
from datetime import datetime, timedelta
from typing import Optional, Literal

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.services.db import engine

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/bot-activity", response_class=HTMLResponse)
async def bot_activity_page(request: Request):
    return templates.TemplateResponse("bot_activity.html", {"request": request})

@router.get("/api/bot-activity/options")
async def bot_activity_options():
    with engine.connect() as conn:
        exchanges = [r[0] for r in conn.execute(text(
            "SELECT DISTINCT exchange FROM bot_activity_log ORDER BY 1"
        )).all()]
        pairs = [r[0] for r in conn.execute(text(
            "SELECT DISTINCT pair FROM bot_activity_log ORDER BY 1"
        )).all()]
        types = [r[0] for r in conn.execute(text(
            "SELECT DISTINCT signal_type FROM bot_activity_log ORDER BY 1"
        )).all()]
    return {"exchanges": exchanges, "pairs": pairs, "signal_types": types}

Bucket = Literal["minute", "hour", "day"]

def _choose_bucket(dt_from: datetime, dt_to: datetime) -> Bucket:
    span = dt_to - dt_from
    if span <= timedelta(days=1):
        return "minute"
    if span <= timedelta(days=7):
        return "hour"
    return "day"

@router.get("/api/bot-activity/data")
async def bot_activity_data(
    exchange: Optional[str] = None,
    pair: Optional[str] = None,
    signal_type: Optional[str] = Query(None, alias="signalType"),
    dt_from: Optional[datetime] = Query(None, alias="from"),
    dt_to: Optional[datetime] = Query(None, alias="to"),
    limit: int = 300,
):
    # за замовчуванням — останні 24 години
    now = datetime.utcnow()
    if not dt_to:
        dt_to = now
    if not dt_from:
        dt_from = dt_to - timedelta(days=1)

    bucket = _choose_bucket(dt_from, dt_to)

    where = ["timestamp BETWEEN :from AND :to"]
    params = {"from": dt_from, "to": dt_to, "limit": limit}
    if exchange:
        where.append("exchange = :exchange")
        params["exchange"] = exchange
    if pair:
        where.append("pair = :pair")
        params["pair"] = pair
    if signal_type:
        where.append("signal_type = :signal_type")
        params["signal_type"] = signal_type
    where_sql = " AND ".join(where)

    rows_sql = f"""
        SELECT id, timestamp, exchange, pair, signal, signal_type
        FROM bot_activity_log
        WHERE {where_sql}
        ORDER BY timestamp DESC
        LIMIT :limit
    """

    agg_sql = f"""
        SELECT date_trunc(:bucket, timestamp) AS ts, count(*) AS cnt
        FROM bot_activity_log
        WHERE {where_sql}
        GROUP BY 1
        ORDER BY 1
    """

    with engine.connect() as conn:
        rows = [dict(r._mapping) for r in conn.execute(text(rows_sql), params).all()]
        agg = [dict(r._mapping) for r in conn.execute(
            text(agg_sql), {**params, "bucket": bucket}
        ).all()]

    return {"bucket": bucket, "rows": rows, "series": agg}
