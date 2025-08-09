from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional, List, Literal
from enum import Enum

Action = Literal["BUY", "SELL"]

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
    action: Optional[Action] = None
    condition_type: Optional[str] = None
    param_1: Optional[str] = None
    param_2: Optional[str] = None
    enabled: Optional[bool] = None
    exchange: Optional[str] = None
    pair: Optional[str] = None
    priority: Optional[int] = None

class StrategyRuleCreate(StrategyRuleBase):
    action: Action
    condition_type: str

class StrategyRuleUpdate(StrategyRuleBase):
    pass

class StrategyRuleResponse(StrategyRuleBase):
    id: int