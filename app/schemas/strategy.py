from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional, List
from enum import Enum

from app.services.db import database
from app.models import strategy_rules
from app.dependencies import get_current_user

# ===== Enums =====
class ActionEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class ConditionTypeEnum(str, Enum):
    RSI_ABOVE = "RSI_ABOVE"
    RSI_BELOW = "RSI_BELOW"
    # Додай інші типи умов за потреби


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

class StrategyRuleResponse(StrategyRuleBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
