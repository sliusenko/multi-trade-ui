from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional, List
from app.services.db import database
from app.models import strategy_rules
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/strategy_rules", tags=["Strategy Rules"])


# ===== Schemas =====
class StrategyRuleBase(BaseModel):
    action: str
    condition_type: str
    param_1: Optional[float] = None
    param_2: Optional[float] = None
    enabled: bool
    exchange: str
    pair: str
    priority: Optional[int] = None


class StrategyRuleCreate(StrategyRuleBase):
    pass


class StrategyRuleUpdate(StrategyRuleBase):
    pass


class StrategyRuleOut(StrategyRuleBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# ===== Routes =====

@router.get("/", response_model=List[StrategyRuleOut])
async def get_rules(current_user_id: int = Depends(get_current_user)):
    """Отримати всі правила користувача"""
    query = select(strategy_rules).where(strategy_rules.c.user_id == current_user_id)
    rows = await database.fetch_all(query)
    return rows


@router.post("/", response_model=dict)
async def create_rule(
    rule: StrategyRuleCreate,
    current_user_id: int = Depends(get_current_user)
):
    """Створити нове правило"""
    query = strategy_rules.insert().values(
        user_id=current_user_id,
        action=rule.action,
        condition_type=rule.condition_type,
        param_1=rule.param_1,
        param_2=rule.param_2,
        enabled=rule.enabled,
        exchange=rule.exchange,
        pair=rule.pair,
        priority=rule.priority
    )
    new_id = await database.execute(query)
    return {"id": new_id, "status": "created"}


@router.put("/{rule_id}", response_model=dict)
async def update_rule(
    rule_id: int,
    rule: StrategyRuleUpdate,
    current_user_id: int = Depends(get_current_user)
):
    """Оновити правило"""
    query = (
        strategy_rules.update()
        .where(strategy_rules.c.id == rule_id)
        .where(strategy_rules.c.user_id == current_user_id)
        .values(
            action=rule.action,
            condition_type=rule.condition_type,
            param_1=rule.param_1,
            param_2=rule.param_2,
            enabled=rule.enabled,
            exchange=rule.exchange,
            pair=rule.pair,
            priority=rule.priority
        )
    )
    result = await database.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "updated", "id": rule_id}


@router.delete("/{rule_id}", response_model=dict)
async def delete_rule(rule_id: int, current_user_id: int = Depends(get_current_user)):
    """Видалити правило"""
    query = (
        strategy_rules.delete()
        .where(strategy_rules.c.id == rule_id)
        .where(strategy_rules.c.user_id == current_user_id)
    )
    result = await database.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "deleted", "id": rule_id}
