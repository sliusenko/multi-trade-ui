from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from typing import Optional, List, Literal, Union
from enum import Enum
from decimal import Decimal

Action = Literal["BUY", "SELL"]
Param = Optional[Union[int, float, Decimal, str]]

# ===== Enums =====
class ActionEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class ConditionTypeEnum(str, Enum):
    RSI_ABOVE = "RSI_ABOVE"
    RSI_BELOW = "RSI_BELOW"
    BLOCK_TRADE_INTERVAL ="BLOCK_TRADE_INTERVAL"
    BLOCK_VOLATILITY_GT = "BLOCK_VOLATILITY_GT"
    REQUIRE_POSITION_ROOM_USD_LT = "REQUIRE_POSITION_ROOM_USD_LT"
    RSI_Z_LT = "RSI_Z_LT"
    VOLUME_Z_GT_AND_PRICE_Z_LT0 ="VOLUME_Z_GT_AND_PRICE_Z_LT0"
    TREND_DIP_STRONG = "TREND_DIP_STRONG"
    OVERBOUGHT ="OVERBOUGHT"
    BB_SELL ="BB_SELL"
    DEAD_CROSS = "DEAD_CROSS"

# ===== Schemas =====
class StrategyRuleBase(BaseModel):
    action: ActionEnum
    condition_type: ConditionTypeEnum
    param_1: Optional[float] = None
    param_2: Optional[float] = None
    enabled: bool
    exchange: str
    pair: str
    priority: Optional[int] = None

class StrategyRuleCreate(StrategyRuleBase):
    pass

class StrategyRuleUpdate(StrategyRuleBase):
    pass

class StrategyRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # замість orm_mode у v2

    id: int
    action: Action
    condition_type: str          # вже виправили на str
    param_1: Param = None        # ← замість str
    param_2: Param = None        # ← замість str
    enabled: bool
    exchange: Optional[str] = None
    pair: Optional[str] = None
    priority: Optional[int] = None