# app/schemas/strategy_sets.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal, Union
from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal

Action = Literal["BUY", "SELL"]
Param  = Optional[Union[int, float, Decimal, str]]

class StrategySetBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = False
    exchange: Optional[str] = None
    pair: Optional[str] = None

class StrategySetCreate(StrategySetBase): pass

class StrategySetUpdate(StrategySetBase): pass

class StrategySetResponse(StrategySetBase):
    id: int
    class Config: orm_mode = True

class StrategySetBase(BaseModel):
  name: Optional[str] = None
  description: Optional[str] = None
  exchange: Optional[str] = None
  pair: Optional[str] = None
  active: Optional[bool] = None

# app/schemas/strategy_sets_rules.py
class SetRuleCreate(BaseModel):
    rule_id: int
    enabled: bool = True
    priority: int = Field(ge=0, default=100)

class SetRuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)

class SetRuleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rule_id: int
    action: Action
    condition_type: str
    param_1: Param = None
    param_2: Param = None
    enabled: bool
    priority: int

class StrategySetRuleBase(BaseModel):
    set_id: int
    rule_id: int
    enabled: bool = True
    override_priority: Optional[int] = None

class StrategySetRuleCreate(StrategySetRuleBase): pass

class StrategySetRuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    override_priority: Optional[int] = None

class StrategySetRuleResponse(StrategySetRuleBase): pass


# app/schemas/strategy_weights.py
class StrategyWeightsBase(BaseModel):
    exchange: str
    pair: str
    rsi_weight: float = 1.0
    forecast_weight: float = 1.0
    acceleration_weight: float = 1.0
    trade_logic: str = "COMBINER"

class StrategyWeightsCreate(StrategyWeightsBase): pass

class StrategyWeightsUpdate(BaseModel):
    rsi_weight: Optional[float] = None
    forecast_weight: Optional[float] = None
    acceleration_weight: Optional[float] = None
    trade_logic: Optional[str] = None

class StrategyWeightsResponse(StrategyWeightsBase):
    user_id: int
    updated_at: Optional[str]
