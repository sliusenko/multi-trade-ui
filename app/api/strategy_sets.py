from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from typing import List
from app.services.db import database
from app.models import strategy_sets, strategy_set_rules, strategy_rules
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/strategy_sets", tags=["Strategy Sets"])

@router.get("", response_model=list)
async def list_sets(current_user_id: int = Depends(get_current_user)):
    q = select(strategy_sets).where(strategy_sets.c.user_id == current_user_id)
    return await database.fetch_all(q)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_set(payload: dict, current_user_id: int = Depends(get_current_user)):
    vals = {**payload, "user_id": current_user_id}
    new_id = await database.execute(insert(strategy_sets).values(**vals).returning(strategy_sets.c.id))
    row = await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == new_id))
    return row

@router.put("/{set_id}")
async def update_set(set_id: int, payload: dict, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        update(strategy_sets)
        .where((strategy_sets.c.id == set_id) & (strategy_sets.c.user_id == current_user_id))
        .values(**payload)
    )
    return await database.fetch_one(select(strategy_sets).where(strategy_sets.c.id == set_id))

@router.delete("/{set_id}", status_code=204)
async def delete_set(set_id: int, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        delete(strategy_sets).where((strategy_sets.c.id == set_id) & (strategy_sets.c.user_id == current_user_id))
    )
