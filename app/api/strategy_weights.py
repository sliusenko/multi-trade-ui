from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, delete, update, func
from sqlalchemy.dialects.postgresql import insert
from app.services.db import database
from app.dependencies import get_current_user
from app.models import strategy_weights  # SQLAlchemy Table

router = APIRouter(prefix="/api/strategy_weights", tags=["Strategy Weights"])

class WeightsBase(BaseModel):
    exchange: Optional[str] = None
    pair: Optional[str] = None
    rsi_weight: Optional[float] = Field(default=1.0)
    forecast_weight: Optional[float] = Field(default=1.0)
    acceleration_weight: Optional[float] = Field(default=1.0)
    trade_logic: Optional[str] = Field(default="COMBINER")

class WeightsUpsert(WeightsBase):
    exchange: str
    pair: str

class WeightsResponse(WeightsBase):
    updated_at: Optional[str] = None

@router.get("", response_model=List[WeightsResponse])
@router.get("/", response_model=List[WeightsResponse])
async def list_weights(current_user_id: int = Depends(get_current_user)):
    q = (
        select(strategy_weights)
        .where(strategy_weights.c.user_id == current_user_id)
        .order_by(strategy_weights.c.exchange, strategy_weights.c.pair)
    )
    rows = await database.fetch_all(q)
    return [WeightsResponse(**dict(r)) for r in rows]

@router.put("", response_model=WeightsResponse, status_code=status.HTTP_200_OK)
@router.put("/", response_model=WeightsResponse, status_code=status.HTTP_200_OK)
async def upsert_weights(payload: WeightsUpsert, current_user_id: int = Depends(get_current_user)):
    data = payload.dict()
    data["user_id"] = current_user_id

    stmt = insert(strategy_weights).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=[strategy_weights.c.user_id, strategy_weights.c.exchange, strategy_weights.c.pair],
        set_={
            "rsi_weight": stmt.excluded.rsi_weight,
            "forecast_weight": stmt.excluded.forecast_weight,
            "acceleration_weight": stmt.excluded.acceleration_weight,
            "trade_logic": stmt.excluded.trade_logic,
            "updated_at": func.now(),
        },
    )
    await database.execute(stmt)

    row = await database.fetch_one(
        select(strategy_weights).where(
            strategy_weights.c.user_id == current_user_id,
            strategy_weights.c.exchange == data["exchange"],
            strategy_weights.c.pair == data["pair"],
        )
    )
    return WeightsResponse(**dict(row))

@router.delete("/{exchange}/{pair}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weights(exchange: str, pair: str, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        delete(strategy_weights).where(
            strategy_weights.c.user_id == current_user_id,
            strategy_weights.c.exchange == exchange,
            strategy_weights.c.pair == pair,
        )
    )
