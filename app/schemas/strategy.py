from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from typing import Optional, List, Literal, Union
from enum import Enum
from decimal import Decimal


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

Action = Literal["BUY", "SELL"]
Param = Optional[Union[int, float, Decimal, str]]  # ← ключова зміна

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