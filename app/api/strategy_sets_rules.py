# app/routers/strategy_sets_rules.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.strategy_sets import SetRuleItem, SetRuleUpdate, SetRuleCreate, ReorderPayload
from app.services.db import database
from app.models import strategy_sets_rules, strategy_rules, strategy_sets
from app.dependencies import get_current_user, is_admin_user, _resolve_user_scope
from sqlalchemy import select, insert, update, delete, text, distinct, and_

router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Set Rules"])

# ---- helpers ----
_ALL_TOKENS = {"", "all", "any", "all pairs", "all users", "all exchanges", "null", "-"}

def _normalize_exchange(ex: str | None) -> str | None:
    if ex is None:
        return None
    ex_norm = ex.strip().lower()
    return None if ex_norm in _ALL_TOKENS else ex_norm

def _normalize_pair(p: str | None) -> str | None:
    if p is None:
        return None
    p_norm = p.strip()
    # приймаємо як плейсхолдери: "", "all", "All Pairs", "-", "null"
    return None if p_norm.lower() in _ALL_TOKENS else p_norm.upper()

# ---- core без Query/Depends ----
async def list_set_rules_core(set_id: int, uid: int, exchange: str | None, pair: str | None):
    ex = _normalize_exchange(exchange)
    pr = _normalize_pair(pair)

    exists_q = select(strategy_sets.c.id).where(
        strategy_sets.c.id == set_id,
        strategy_sets.c.user_id == uid,
    )
    if ex is not None:
        exists_q = exists_q.where(strategy_sets.c.exchange == ex)
    if pr is not None:
        exists_q = exists_q.where(strategy_sets.c.pair == pr)
    if not await database.fetch_one(exists_q):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")

    q = (
        select(
            strategy_sets_rules.c.rule_id,
            strategy_rules.c.action,
            strategy_rules.c.condition_type,
            strategy_rules.c.param_1,
            strategy_rules.c.param_2,
            strategy_sets_rules.c.enabled,
            strategy_sets_rules.c.priority,
        )
        .select_from(
            strategy_sets_rules
            .join(strategy_sets, strategy_sets.c.id == strategy_sets_rules.c.set_id)
            .join(strategy_rules, strategy_rules.c.id == strategy_sets_rules.c.rule_id)
        )
        .where(strategy_sets.c.id == set_id, strategy_sets.c.user_id == uid)
        .order_by(strategy_sets_rules.c.priority, strategy_rules.c.id)
    )
    if ex is not None:
        q = q.where(strategy_sets.c.exchange == ex)
    if pr is not None:
        q = q.where(strategy_sets.c.pair == pr)

    rows = await database.fetch_all(q)
    return [SetRuleItem(**dict(r)) for r in rows]

@router.get("/{set_id}/rules", response_model=List[SetRuleItem])
async def list_set_rules(
    set_id: int,
    user_id: int | None = Query(None),
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    uid = _resolve_user_scope(user_id, current_user_id, admin)
    return await list_set_rules_core(set_id, uid, exchange, pair)

@router.patch("/{set_id}/rules/{rule_id}", response_model=SetRuleItem)
async def update_set_rule(
    set_id: int,
    rule_id: int,
    body: SetRuleUpdate,
    user_id: int | None = Query(None),
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    # сформувати апдейт і повернути щось, щоб зрозуміти, чи був апдейт
    upd = (
        update(strategy_sets_rules)
        .where(
            strategy_sets_rules.c.user_id == uid,
            strategy_sets_rules.c.set_id == set_id,
            strategy_sets_rules.c.rule_id == rule_id,
        )
        .values({k: v for k, v in body.dict(exclude_unset=True).items()})
        .returning(strategy_sets_rules.c.rule_id)
    )

    row = await database.fetch_one(upd)  # <= а не execute()
    if row is None:
        raise HTTPException(404, "Link not found")

    items = await list_set_rules_core(set_id, uid, exchange, pair)
    return next(i for i in items if i.rule_id == rule_id)

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

@router.post("/{set_id}/rules", response_model=SetRuleItem, status_code=status.HTTP_201_CREATED)
async def add_set_rule(
    set_id: int,
    body: SetRuleCreate,
    user_id: int | None = Query(None),
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    rule_ok = await database.fetch_one(
        select(strategy_rules.c.id).where(
            strategy_rules.c.id == body.rule_id,
            strategy_rules.c.user_id == uid,
        )
    )
    set_ok = await database.fetch_one(
        select(strategy_sets.c.id).where(
            strategy_sets.c.id == set_id,
            strategy_sets.c.user_id == uid,
        )
    )
    if not rule_ok or not set_ok:
        raise HTTPException(404, "Rule or Set not found")

    exists = await database.fetch_one(
        select(strategy_sets_rules.c.rule_id).where(
            strategy_sets_rules.c.user_id == uid,
            strategy_sets_rules.c.set_id == set_id,
            strategy_sets_rules.c.rule_id == body.rule_id,
        )
    )
    if exists:
        raise HTTPException(409, "Rule already attached to this set")

    await database.execute(
        insert(strategy_sets_rules).values(
            user_id=uid,
            set_id=set_id,
            rule_id=body.rule_id,
            enabled=body.enabled,
            priority=body.priority,
        )
    )

    items = await list_set_rules_core(set_id, uid, exchange, pair)   # ✅
    return next(i for i in items if i.rule_id == body.rule_id)
