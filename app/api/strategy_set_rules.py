from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from app.services.db import database
from app.models import strategy_set_rules, strategy_sets
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/strategy_set_rules", tags=["Strategy Set Rules"])

@router.get("/{set_id}")
async def list_set_rules(set_id: int, current_user_id: int = Depends(get_current_user)):
    owner = await database.fetch_one(select(strategy_sets.c.user_id).where(strategy_sets.c.id == set_id))
    if not owner or owner.user_id != current_user_id:
        raise HTTPException(status_code=404, detail="Set not found")
    q = select(strategy_set_rules).where(strategy_set_rules.c.set_id == set_id)
    return await database.fetch_all(q)

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_rule(payload: dict, current_user_id: int = Depends(get_current_user)):
    # опційно: перевірка власності сету
    await database.execute(insert(strategy_set_rules).values(**payload))
    return payload

@router.put("/{set_id}/{rule_id}")
async def update_rule(set_id: int, rule_id: int, patch: dict, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        update(strategy_set_rules)
        .where((strategy_set_rules.c.set_id == set_id) & (strategy_set_rules.c.rule_id == rule_id))
        .values(**patch)
    )
    row = await database.fetch_one(
        select(strategy_set_rules).where(
            (strategy_set_rules.c.set_id == set_id) & (strategy_set_rules.c.rule_id == rule_id)
        )
    )
    return row

@router.delete("/{set_id}/{rule_id}", status_code=204)
async def remove_rule(set_id: int, rule_id: int, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        delete(strategy_set_rules)
        .where((strategy_set_rules.c.set_id == set_id) & (strategy_set_rules.c.rule_id == rule_id))
    )
