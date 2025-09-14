# routes/forecast_vs_actual.py
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from config import engine, current_user_id  # якщо маєш helper

bp = Blueprint("forecast_vs_actual", __name__)

VALID_INTERVALS = {
    "1h":  "1 hour",
    "4h":  "4 hours",
    "12h": "12 hours",
    "1d":  "1 day",
    "3d":  "3 days",
}

@bp.get("/api/forecast_vs_actual_long")
def forecast_vs_actual_long():
    exchange   = (request.args.get("exchange") or "").lower()
    pair       = (request.args.get("pair") or "").upper()
    timeframe  = (request.args.get("timeframe") or "").lower()  # для заголовку/відображення
    interval   = (request.args.get("interval") or "4h").lower()
    flh_tf     = (request.args.get("flh_timeframe") or "5m").lower()
    user_id    = request.args.get("user_id", type=int) or current_user_id()

    if interval not in VALID_INTERVALS:
        return jsonify({"error": "invalid interval", "allowed": list(VALID_INTERVALS)}), 400

    sql = text("""
        SELECT
            date_trunc('hour', flh.timestamp)      AS ts_hour,
            AVG(flh.predicted_price)               AS predicted_price,
            AVG(ph.price)                          AS actual_price
        FROM forecast_longterm_history flh
        JOIN analysis_data ph
          ON  flh.pair      = ph.pair
          AND flh.exchange  = ph.exchange
          AND flh.user_id   = ph.user_id
          AND ph.timeframe  = flh.timeframe
          AND date_trunc('minute', flh.timestamp) = date_trunc('minute', ph.timestamp)
        WHERE flh.pair       = :pair
          AND flh.exchange   = :exchange
          AND flh.user_id    = :user_id
          AND flh.timeframe  = :flh_timeframe
          AND flh.timestamp BETWEEN NOW() - (:interval)::interval AND NOW()
        GROUP BY ts_hour
        ORDER BY ts_hour
    """)

    with engine.connect() as conn:
        rows = conn.execute(sql, {
            "pair": pair,
            "exchange": exchange,
            "user_id": user_id,
            "flh_timeframe": flh_tf,
            "interval": VALID_INTERVALS[interval],
        }).mappings().all()

    data = [
        {
            "ts": r["ts_hour"].isoformat(),
            "predicted_price": float(r["predicted_price"]) if r["predicted_price"] is not None else None,
            "actual_price": float(r["actual_price"]) if r["actual_price"] is not None else None,
        }
        for r in rows
    ]
    return jsonify({
        "exchange": exchange, "pair": pair, "timeframe": timeframe,
        "interval": interval, "flh_timeframe": flh_tf, "points": data
    })
