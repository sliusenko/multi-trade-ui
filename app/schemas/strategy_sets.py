# app/schemas/strategy_sets.py
from pydantic import BaseModel
from typing import Optional, List

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


# app/schemas/strategy_set_rules.py
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
