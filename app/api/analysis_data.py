from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.db import database  # використовуй твій існуючий database з'єднувач

router = APIRouter(prefix="/api", tags=["analysis_data"])

# ——— модель відповіді
class AnalysisRow(BaseModel):
    timestamp: datetime
    price: Optional[float] = None
    change: Optional[float] = None
    rsi: Optional[float] = None
    rsi_z: Optional[float] = None
    rsi_z_sell_threshold: Optional[float] = None
    rsi_z_buy_threshold: Optional[float] = None
    volume: Optional[float] = None
    ma_vol_5: Optional[float] = None
    ma_vol_10: Optional[float] = None
    avg_volume: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_prev: Optional[float] = None
    macd_signal_prev: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    volatility: Optional[float] = None
    delta_price: Optional[float] = None
    acceleration: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    price_z: Optional[float] = None
    volume_z: Optional[float] = None
    macd_diff_z: Optional[float] = None
    volatility_z: Optional[float] = None
    sma_50_trend: Optional[int] = None
    sma_200_trend: Optional[int] = None
    sma_50_trend_strength: Optional[float] = None
    sma_200_trend_strength: Optional[float] = None

def _parse_period(period: Optional[str]) -> Optional[timedelta]:
    if not period:
        return None
    try:
        if period.endswith("d"):
            return timedelta(days=int(period[:-1]))
        if period.endswith("h"):
            return timedelta(hours=int(period[:-1]))
        if period.endswith("m"):
            return timedelta(minutes=int(period[:-1]))
    except Exception:
        return None
    return None

@router.get("/analysis_data", response_model=List[AnalysisRow])
async def list_analysis_data(
    user_id: Optional[int] = Query(None),
    exchange: Optional[str] = Query(None),
    pair: Optional[str] = Query(None),
    timeframe: Optional[str] = Query(None),
    bb_period: Optional[int] = Query(None),
    rsi_period: Optional[int] = Query(None),
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = Query(None),
    period: Optional[str] = Query(None, description="швидкий діапазон: 1d, 7d, 24h, 90m"),
    limit: int = Query(5000, ge=1, le=50000),
) -> List[AnalysisRow]:
    """
    Повертає ряди з таблиці analysis_data з фільтрами.
    Сортування: ASC за timestamp.
    """
    # часовий діапазон
    if period and not from_ and not to:
        td = _parse_period(period)
        if td is not None:
            to = datetime.now(timezone.utc)
            from_ = to - td

    where = []
    params: Dict[str, Any] = {}

    if user_id is not None:
        where.append('user_id = :user_id')
        params['user_id'] = user_id
    if exchange:
        where.append('exchange = :exchange')
        params['exchange'] = exchange
    if pair:
        where.append('pair = :pair')
        params['pair'] = pair
    if timeframe:
        where.append('timeframe = :timeframe')
        params['timeframe'] = timeframe
    if bb_period is not None:
        where.append('bb_period = :bb_period')
        params['bb_period'] = bb_period
    if rsi_period is not None:
        where.append('rsi_period = :rsi_period')
        params['rsi_period'] = rsi_period
    if from_:
        where.append('"timestamp" >= :from_ts')
        params['from_ts'] = from_
    if to:
        where.append('"timestamp" <= :to_ts')
        params['to_ts'] = to

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT
          "timestamp", price, change, rsi, rsi_z, rsi_z_sell_threshold, rsi_z_buy_threshold,
          volume, ma_vol_5, ma_vol_10, avg_volume, macd, macd_signal, macd_prev,
          macd_signal_prev, sma_50, sma_200, volatility, delta_price, acceleration,
          open, close, high, low, price_z, volume_z, macd_diff_z, volatility_z,
          sma_50_trend, sma_200_trend, sma_50_trend_strength, sma_200_trend_strength
        FROM analysis_data
        {where_sql}
        ORDER BY "timestamp" ASC
        LIMIT :limit
    """
    params["limit"] = limit

    rows = await database.fetch_all(query=sql, values=params)
    # convert to dicts acceptable by pydantic
    return [AnalysisRow(**dict(r)) for r in rows]
