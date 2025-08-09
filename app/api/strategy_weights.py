from fastapi import APIRouter, Depends, status
from sqlalchemy import select, insert
from app.services.db import database
from app.models import strategy_weights
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/strategy_weights", tags=["Strategy Weights"])

@router.get("")
async def list_weights(current_user_id: int = Depends(get_current_user)):
    q = select(strategy_weights).where(strategy_weights.c.user_id == current_user_id)
    return await database.fetch_all(q)

@router.post("", status_code=status.HTTP_201_CREATED)
async def upsert_weights(payload: dict, current_user_id: int = Depends(get_current_user)):
    values = {**payload, "user_id": current_user_id}
    # upsert по PK (user_id, exchange, pair)
    q = strategy_weights.insert().values(**values).on_conflict_do_update(
        index_elements=["user_id", "exchange", "pair"],
        set_=values
    )
    await database.execute(q)
    row = await database.fetch_one(select(strategy_weights).where(
        (strategy_weights.c.user_id == current_user_id) &
        (strategy_weights.c.exchange == payload["exchange"]) &
        (strategy_weights.c.pair == payload["pair"])
    ))
    return row

@router.delete("/{exchange}/{pair}", status_code=204)
async def delete_weights(exchange: str, pair: str, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        strategy_weights.delete().where(
            (strategy_weights.c.user_id == current_user_id) &
            (strategy_weights.c.exchange == exchange) &
            (strategy_weights.c.pair == pair)
        )
    )
