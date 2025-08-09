from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, text
from typing import Optional, List
from app.schemas.strategy_sets import (
    StrategySetResponse,
    StrategySetCreate,
    StrategySetUpdate
)
from app.services.db import database
from app.models import strategy_sets
from app.dependencies import get_current_user


# app/routes/strategy_sets.py
router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Sets"])

@router.get("", response_model=List[StrategySetResponse])
async def list_sets(current_user_id: int = Depends(get_current_user)):
    q = select(strategy_sets).where(strategy_sets.c.user_id == current_user_id)
    return await database.fetch_all(q)

@router.post("", response_model=StrategySetResponse, status_code=201)
async def create_set(payload: StrategySetCreate, current_user_id: int = Depends(get_current_user)):
    values = payload.dict()
    values["user_id"] = current_user_id
    new_id = await database.execute(strategy_sets.insert().values(**values).returning(strategy_sets.c.id))
    row = await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == new_id))
    return row

@router.put("/{set_id}", response_model=StrategySetResponse)
async def update_set(set_id: int, payload: StrategySetUpdate, current_user_id: int = Depends(get_current_user)):
    q = strategy_sets.update().where(
        (strategy_sets.c.id == set_id) & (strategy_sets.c.user_id == current_user_id)
    ).values(**payload.dict())
    await database.execute(q)
    return await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == set_id))

@router.delete("/{set_id}", status_code=204)
async def delete_set(set_id: int, current_user_id: int = Depends(get_current_user)):
    await database.execute(strategy_sets.delete().where(
        (strategy_sets.c.id == set_id) & (strategy_sets.c.user_id == current_user_id)
    ))
