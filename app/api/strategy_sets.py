from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy import select, update, delete, text, distinct, and_
from app.services.db import database
from app.dependencies import get_current_user, is_admin_user
from app.models import strategy_sets  # SQLAlchemy Table

from pydantic import BaseModel

router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Sets"])

class StrategySetBase(BaseModel):
  name: Optional[str] = None
  description: Optional[str] = None
  exchange: Optional[str] = None
  pair: Optional[str] = None
  active: Optional[bool] = None

class StrategySetCreate(StrategySetBase):
  name: str

class StrategySetUpdate(StrategySetBase):
  pass

class StrategySetResponse(StrategySetBase):
  id: int

def _normalize_exchange(ex: str | None) -> str | None:
    return ex.lower() if ex else None

def _normalize_pair(p: str | None) -> str | None:
    return p.upper() if p else None

def _resolve_user_scope(
    requested_user_id: int | None,
    current_user_id: int,
    is_admin: bool,
) -> int:
    if requested_user_id is None or requested_user_id == current_user_id:
        return current_user_id
    if not is_admin:
        # не дозволяємо дивитись чужі дані
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return requested_user_id

@router.get("/", response_model=list[StrategySetResponse])
@router.get("",  response_model=list[StrategySetResponse])
async def list_sets(
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    user_id: int | None = Query(None),                 # <- додаємо
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),              # <- твоя перевірка адміна
):
    ex = _normalize_exchange(exchange)
    pr = _normalize_pair(pair)
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    stmt = (
        select(strategy_sets)
        .where(strategy_sets.c.user_id == uid)
        .order_by(strategy_sets.c.id)
    )
    if ex:
        stmt = stmt.where(strategy_sets.c.exchange == ex)
    if pr:
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
async def update_set(set_id: int, payload: StrategySetUpdate, current_user_id: int = Depends(get_current_user)):
  values = {k:v for k,v in payload.dict(exclude_unset=True).items()}
  await database.execute(
    update(strategy_sets).where(
      strategy_sets.c.id == set_id, strategy_sets.c.user_id == current_user_id
    ).values(**values)
  )
  row = await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == set_id))
  if not row: raise HTTPException(status_code=404, detail="Set not found")
  return StrategySetResponse(**dict(row))

@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(set_id: int, current_user_id: int = Depends(get_current_user)):
  await database.execute(
    delete(strategy_sets).where(
      strategy_sets.c.id == set_id, strategy_sets.c.user_id == current_user_id
    )
  )

