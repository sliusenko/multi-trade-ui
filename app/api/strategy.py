from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select
from app.services.db import database
from app.models import strategy_rules

router = APIRouter()

# ===== Schemas =====
class RuleBase(BaseModel):
    action: str
    condition_type: str
    enabled: bool

class RuleCreate(RuleBase):
    pass

class RuleUpdate(RuleBase):
    pass

# ===== CRUD Endpoints =====

class StrategyRuleCreate(BaseModel):
    action: str        # BUY / SELL
    condition: str     # RSI_BELOW / RSI_ABOVE
    value: Optional[float] = None
    # user_id тут більше не передаємо


@router.post("/strategy_rules")
async def create_rule(
    rule: StrategyRuleCreate,
    current_user_id: int = Depends(get_current_user),
):
    query = strategy_rules.insert().values(
        user_id=current_user_id,
        action=rule.action,
        condition=rule.condition,
        value=rule.value
    )
    new_id = await database.execute(query)
    return {"id": new_id, "status": "created"}

@router.put("/strategy_rules/{rule_id}")
async def update_rule(rule_id: int, rule: RuleUpdate):
    query = strategy_rules.update().where(strategy_rules.c.id == rule_id).values(
        action=rule.action,
        condition_type=rule.condition_type,
        enabled=rule.enabled
    )
    await database.execute(query)
    return {"status": "updated", "id": rule_id}

@router.delete("/strategy_rules/{rule_id}")
async def delete_rule(rule_id: int):
    query = strategy_rules.delete().where(strategy_rules.c.id == rule_id)
    await database.execute(query)
    return {"status": "deleted", "id": rule_id}
