from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from typing import Optional, List, Literal
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

Action = Literal["BUY", "SELL"]

class StrategyRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # замість orm_mode в Pydantic v2

    id: int
    action: Action
    # було: condition_type: Literal["RSI_ABOVE", "RSI_BELOW"]
    # стало: просто рядок, щоб підтримати всі наші нові типи:
    condition_type: str

    # якщо типи параметрів плавають — залиш прості Optional:
    param_1: Optional[str] = None
    param_2: Optional[str] = None
    enabled: bool
    exchange: Optional[str] = None
    pair: Optional[str] = None
    priority: Optional[int] = None