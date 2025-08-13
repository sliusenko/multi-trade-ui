from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import select, delete, update, func, text, distinct, and_
from sqlalchemy.dialects.postgresql import insert

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
    updated_at: datetime | None = None