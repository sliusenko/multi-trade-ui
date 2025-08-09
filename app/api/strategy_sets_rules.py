# app/routers/strategy_sets_rules.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.strategy_sets import SetRuleItem, SetRuleUpdate
from app.services.db import database
from app.models import strategy_sets_rules, strategy_rules, strategy_sets
from app.dependencies import get_current_user
from sqlalchemy import select, insert, update, delete

router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Set Rules"])

@router.get("/{set_id}/rules", response_model=List[SetRuleItem])
async def list_set_rules(set_id: int, uid: int = Depends(get_current_user)):
    # перевіримо право доступу до сету
    exists_q = select(strategy_sets.c.id).where(
        strategy_sets.c.id == set_id, strategy_sets.c.user_id == uid
    )
    if not await database.fetch_one(exists_q):
        raise HTTPException(404, "Set not found")

    q = (
        select(
            strategy_sets_rules.c.rule_id,
            strategy_rules.c.action,
            strategy_rules.c.condition_type,
            strategy_rules.c.param_1,
            strategy_rules.c.param_2,
            strategy_sets_rules.c.enabled,
            strategy_sets_rules.c.priority,
#            strategy_sets_rules.c.note,
        )
        .select_from(strategy_sets_rules.join(
            strategy_rules, strategy_rules.c.id == strategy_sets_rules.c.rule_id
        ))
        .where(
            strategy_sets_rules.c.user_id == uid,
            strategy_sets_rules.c.set_id == set_id,
        )
        .order_by(strategy_sets_rules.c.priority, strategy_rules.c.id)
    )
    rows = await database.fetch_all(q)
    return [SetRuleItem(**dict(r)) for r in rows]

@router.post("/{set_id}/rules", response_model=SetRuleItem, status_code=status.HTTP_201_CREATED)
async def add_set_rule(set_id: int, body: SetRuleCreate, uid: int = Depends(get_current_user)):
    # валідність rule і володіння
    rule_ok = await database.fetch_one(
        select(strategy_rules.c.id).where(
            strategy_rules.c.id == body.rule_id, strategy_rules.c.user_id == uid
        )
    )
    set_ok = await database.fetch_one(
        select(strategy_sets.c.id).where(
            strategy_sets.c.id == set_id, strategy_sets.c.user_id == uid
        )
    )
    if not rule_ok or not set_ok:
        raise HTTPException(404, "Rule or Set not found")

    # унікальність у межах (user,set,rule)
    exists = await database.fetch_one(
        select(strategy_sets_rules.c.rule_id).where(
            strategy_sets_rules.c.user_id == uid,
            strategy_sets_rules.c.set_id == set_id,
            strategy_sets_rules.c.rule_id == body.rule_id,
        )
    )
    if exists:
        raise HTTPException(409, "Rule already attached to this set")

    ins = (
        insert(strategy_sets_rules)
        .values(
            user_id=uid,
            set_id=set_id,
            rule_id=body.rule_id,
            enabled=body.enabled,
            priority=body.priority,
#            note=body.note,
        )
        .returning(strategy_sets_rules.c.rule_id)
    )
    await database.execute(ins)
    # повернемо повний рядок через list_set_rules
    items = await list_set_rules(set_id, uid)  # reuse
    return next(i for i in items if i.rule_id == body.rule_id)

@router.patch("/{set_id}/rules/{rule_id}", response_model=SetRuleItem)
async def update_set_rule(set_id: int, rule_id: int, body: SetRuleUpdate, uid: int = Depends(get_current_user)):
    upd = (
        update(strategy_sets_rules)
        .where(
            strategy_sets_rules.c.user_id == uid,
            strategy_sets_rules.c.set_id == set_id,
            strategy_sets_rules.c.rule_id == rule_id,
        )
        .values({k: v for k, v in body.dict(exclude_unset=True).items()})
    )
    res = await database.execute(upd)
    if res is None:
        raise HTTPException(404, "Link not found")
    items = await list_set_rules(set_id, uid)
    return next(i for i in items if i.rule_id == rule_id)

class ReorderPayload(BaseModel):
    rule_ids: List[int]

@router.post("/{set_id}/rules/reorder")
async def reorder_rules(set_id: int, payload: ReorderPayload, uid: int = Depends(get_current_user)):
    # простий масовий апдейт: priority = позиція у списку * 10
    prio_map = {rid: (i + 1) * 10 for i, rid in enumerate(payload.rule_ids)}
    async with database.transaction():
        for rid, pr in prio_map.items():
            await database.execute(
                update(strategy_sets_rules)
                .where(
                    strategy_sets_rules.c.user_id == uid,
                    strategy_sets_rules.c.set_id == set_id,
                    strategy_sets_rules.c.rule_id == rid,
                )
                .values(priority=pr)
            )
    return {"status": "ok"}

@router.delete("/{set_id}/rules/{rule_id}", status_code=204)
async def detach_rule(set_id: int, rule_id: int, uid: int = Depends(get_current_user)):
    delq = delete(strategy_sets_rules).where(
        strategy_sets_rules.c.user_id == uid,
        strategy_sets_rules.c.set_id == set_id,
        strategy_sets_rules.c.rule_id == rule_id,
    )
    await database.execute(delq)
