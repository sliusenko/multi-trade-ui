# app/api/strategy.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.strategy import StrategyRuleCreate, StrategyRuleUpdate, StrategyRuleResponse
from app.dependencies import get_current_user
from sqlalchemy import select, update, delete
from app.services.db import database
from app.models import strategy_rules

router = APIRouter(prefix="/api/strategy_rules", tags=["Strategy Rules"])

# ---- GET (list) ----
@router.get("", response_model=List[StrategyRuleResponse])
@router.get("/", response_model=List[StrategyRuleResponse])
async def get_rules(current_user_id: int = Depends(get_current_user)):
    q = select(strategy_rules).where(strategy_rules.c.user_id == current_user_id)
    rows = await database.fetch_all(q)
    return [StrategyRuleResponse(**dict(r)) for r in rows]

# ---- POST (create) ----
@router.post("", response_model=StrategyRuleResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=StrategyRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: StrategyRuleCreate, current_user_id: int = Depends(get_current_user)):
    data = rule.dict()
    data["user_id"] = current_user_id
    inserted_id = await database.execute(strategy_rules.insert().values(**data))
    row = await database.fetch_one(select(strategy_rules).where(strategy_rules.c.id == inserted_id))
    return StrategyRuleResponse(**dict(row))

# ---- PUT/PATCH (update) ----
@router.put("/{rule_id}", response_model=StrategyRuleResponse)
@router.patch("/{rule_id}", response_model=StrategyRuleResponse)
async def update_rule(rule_id: int, rule: StrategyRuleUpdate, current_user_id: int = Depends(get_current_user)):
    values = {k: v for k, v in rule.dict(exclude_unset=True).items()}
    res = await database.execute(
        update(strategy_rules)
        .where(strategy_rules.c.id == rule_id, strategy_rules.c.user_id == current_user_id)
        .values(**values)
    )
    row = await database.fetch_one(select(strategy_rules).where(strategy_rules.c.id == rule_id))
    if not row:
        raise HTTPException(status_code=404, detail="Rule not found")
    return StrategyRuleResponse(**dict(row))

# ---- DELETE ----
@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: int, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        delete(strategy_rules).where(strategy_rules.c.id == rule_id, strategy_rules.c.user_id == current_user_id)
    )
