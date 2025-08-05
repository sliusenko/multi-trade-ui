from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional
from app.services.db import database
from app.models import strategy_rules
from app.dependencies import get_current_user

router = APIRouter()

class RuleBase(BaseModel):
    action: str
    condition: str
    value: Optional[float] = None
    enabled: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(RuleBase):
    pass

@router.get("/strategy_rules")
async def list_rules(current_user_id: int = Depends(get_current_user)):
    query = select(strategy_rules).where(strategy_rules.c.user_id == current_user_id)
    return await database.fetch_all(query)

@router.post("/strategy_rules")
async def create_rule(
    rule: RuleCreate,
    current_user_id: int = Depends(get_current_user),
):
    query = strategy_rules.insert().values(
        user_id=current_user_id,
        action=rule.action,
        condition=rule.condition,
        value=rule.value,
        enabled=rule.enabled
    )
    new_id = await database.execute(query)
    return {"id": new_id, "status": "created"}

@router.put("/strategy_rules/{rule_id}")
async def update_rule(rule_id: int, rule: RuleUpdate):
    query = strategy_rules.update().where(strategy_rules.c.id == rule_id).values(
        action=rule.action,
        condition=rule.condition,
        value=rule.value,
        enabled=rule.enabled
    )
    await database.execute(query)
    return {"status": "updated", "id": rule_id}

@router.delete("/strategy_rules/{rule_id}")
async def delete_rule(rule_id: int):
    query = strategy_rules.delete().where(strategy_rules.c.id == rule_id)
    await database.execute(query)
    return {"status": "deleted", "id": rule_id}

