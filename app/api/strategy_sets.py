from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy import select, update, delete, text, distinct, and_
from app.services.db import database
from app.dependencies import get_current_user, is_admin_user, _resolve_user_scope
from app.schemas.strategy_sets import StrategySetResponse, StrategySetUpdate, StrategySetCreate
from app.models import strategy_sets  # SQLAlchemy Table
from pydantic import BaseModel

router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Sets"])

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

@router.get("/", response_model=list[StrategySetResponse])
@router.get("",  response_model=list[StrategySetResponse])
async def list_sets(exchange: str | None = Query(None), pair: str | None = Query(None), user_id: int | None = Query(None), current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),):
    ex = _normalize_exchange(exchange)
    pr = _normalize_pair(pair)
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    stmt = select(strategy_sets).where(strategy_sets.c.user_id == uid).order_by(strategy_sets.c.id)
    if ex is not None:
        stmt = stmt.where(strategy_sets.c.exchange == ex)
    if pr is not None:
        stmt = stmt.where(strategy_sets.c.pair == pr)

    rows = await database.fetch_all(stmt)
    return [dict(r) for r in rows]

@router.post("", response_model=StrategySetResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=StrategySetResponse, status_code=status.HTTP_201_CREATED)
async def create_set(payload: StrategySetCreate, current_user_id: int = Depends(get_current_user)):
  data = payload.dict()
  data["user_id"] = current_user_id
  new_id = await database.execute(strategy_sets.insert().values(**data))
  row = await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == new_id))
  return StrategySetResponse(**dict(row))

@router.put("/{set_id}", response_model=StrategySetResponse)
@router.patch("/{set_id}", response_model=StrategySetResponse)
async def update_set(set_id: int, payload: StrategySetUpdate, exchange: str | None = Query(None), pair: str | None = Query(None),
    user_id: int | None = Query(None), current_user_id: int = Depends(get_current_user), admin: bool = Depends(is_admin_user),):
    ex = _normalize_exchange(exchange)
    pr = _normalize_pair(pair)
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    values = payload.dict(exclude_unset=True)
    print(f"🔄 PATCH set_id={set_id} by uid={uid} with values={values}, ex={ex}, pr={pr}")

    stmt = update(strategy_sets).where(strategy_sets.c.id == set_id, strategy_sets.c.user_id == uid)
    if ex is not None:
        stmt = stmt.where(strategy_sets.c.exchange == ex)
    if pr is not None:
        stmt = stmt.where(strategy_sets.c.pair == pr)

    res = await database.execute(stmt.values(**values))
    if res == 0:
        print(f"⚠️  No match: id={set_id}, uid={uid}, ex={ex}, pr={pr} — nothing updated.")
        raise HTTPException(status_code=404, detail="Set not found or not allowed")

    fetch_stmt = select(strategy_sets).where(strategy_sets.c.id == set_id)
    row = await database.fetch_one(fetch_stmt)

    print(f"✅ Updated: {dict(row)}")
    return StrategySetResponse(**dict(row))

@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(
    set_id: int,
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    user_id: int | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    ex = _normalize_exchange(exchange)
    pr = _normalize_pair(pair)
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    stmt = delete(strategy_sets).where(strategy_sets.c.id == set_id, strategy_sets.c.user_id == uid)
    if ex is not None:
        stmt = stmt.where(strategy_sets.c.exchange == ex)
    if pr is not None:
        stmt = stmt.where(strategy_sets.c.pair == pr)

    res = await database.execute(stmt)
    if res == 0:
        raise HTTPException(status_code=404, detail="Set not found or not allowed")

# def filter_sets_base(set_id: int | None, uid: int, ex: str | None, pr: str | None):
#     stmt = select(strategy_sets).where(strategy_sets.c.user_id == uid)
#     if set_id is not None:
#         stmt = stmt.where(strategy_sets.c.id == set_id)
#     if ex:
#         stmt = stmt.where(strategy_sets.c.exchange == ex)
#     if pr:
#         stmt = stmt.where(strategy_sets.c.pair == pr)
#     return stmt
