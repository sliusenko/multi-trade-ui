from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional
from app.services.db import database
from app.models import strategy_rules
from app.dependencies import get_current_user

router = APIRouter()

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

from pydantic import BaseModel

class StrategyRule(BaseModel):
    action: str
    condition_type: str
    param_1: float
    param_2: float
    enabled: bool
    exchange: str
    pair: str
    priority: int

@app.post("/api/strategy_rules")
async def create_strategy_rule(rule: StrategyRule):
    # TODO: вставка в БД
    print("New rule:", rule.dict())
    return {"status": "ok", "rule": rule.dict()}

@router.get("/strategy_rules")
async def get_rules(current_user_id: int = Depends(get_current_user)):
    query = select(strategy_rules).where(strategy_rules.c.user_id == current_user_id)
    return await database.fetch_all(query)


@router.post("/strategy_rules")
async def create_rule(
    rule: StrategyRuleCreate,
    current_user_id: int = Depends(get_current_user)
):
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


@router.put("/strategy_rules/{rule_id}")
async def update_rule(rule_id: int, rule: StrategyRuleUpdate):
    query = (
        strategy_rules.update()
        .where(strategy_rules.c.id == rule_id)
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
    await database.execute(query)
    return {"status": "updated", "id": rule_id}


@router.delete("/strategy_rules/{rule_id}")
async def delete_rule(rule_id: int):
    query = strategy_rules.delete().where(strategy_rules.c.id == rule_id)
    await database.execute(query)
    return {"status": "deleted", "id": rule_id}
