from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from flask import Blueprint, render_template, redirect, url_for
from app.services.db import db  # SQLAlchemy session
from app.models import StrategyRule  # твої ORM-моделі

# Flask Blueprint для рендеру HTML
strategy_bp = Blueprint('strategy', __name__)

# FastAPI Router для REST API
router = APIRouter(prefix="/api", tags=["strategy"])


# -------------------------------
#           HTML PAGE
# -------------------------------
@strategy_bp.route('/strategy_dashboard')
def strategy_dashboard():
    rules = db.session.execute(text("SELECT * FROM strategy_rules ORDER BY id")).fetchall()
    sets = db.session.execute(text("SELECT * FROM strategy_sets ORDER BY id")).fetchall()
    weights = db.session.execute(text(
        "SELECT * FROM strategy_weights ORDER BY user_id, exchange, pair"
    )).fetchall()

    return render_template(
        'strategy_dashboard.html',
        rules=rules,
        sets=sets,
        weights=weights
    )


# -------------------------------
#        CRUD API
# -------------------------------

@router.get("/strategy_rules")
async def get_strategy_rules():
    """Отримати всі правила (JSON)"""
    rules = db.session.query(StrategyRule).all()
    return [r.as_dict() for r in rules]  # потрібно мати as_dict() в моделі


@router.put("/strategy_rules/{rule_id}")
async def update_strategy_rule(rule_id: int, request: Request):
    """Оновити існуюче правило"""
    data = await request.json()
    rule = db.session.query(StrategyRule).get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.action = data.get("action", rule.action)
    rule.condition_type = data.get("condition", rule.condition_type)
    rule.enabled = bool(data.get("enabled", rule.enabled))

    db.session.commit()
    return {"status": "updated"}


@router.delete("/strategy_rules/{rule_id}")
async def delete_strategy_rule(rule_id: int):
    """Видалити правило"""
    rule = db.session.query(StrategyRule).get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.session.delete(rule)
    db.session.commit()
    return {"status": "deleted"}
