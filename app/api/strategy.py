from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class StrategyRule(BaseModel):
    id: int
    name: str
    condition: str
    enabled: bool = True

# Тимчасова пам'ять (замість БД)
STRATEGY_RULES = [
    {"id": 1, "name": "RSI < 30", "condition": "rsi<30", "enabled": True},
    {"id": 2, "name": "RSI > 70", "condition": "rsi>70", "enabled": False},
]

@router.get("/", response_model=list[StrategyRule])
async def get_rules():
    return STRATEGY_RULES

@router.post("/", response_model=StrategyRule)
async def add_rule(rule: StrategyRule):
    STRATEGY_RULES.append(rule.dict())
    return rule

@router.put("/{rule_id}", response_model=StrategyRule)
async def update_rule(rule_id: int, rule: StrategyRule):
    for idx, r in enumerate(STRATEGY_RULES):
        if r["id"] == rule_id:
            STRATEGY_RULES[idx] = rule.dict()
            return rule
    return {"error": "Not found"}

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int):
    global STRATEGY_RULES
    STRATEGY_RULES = [r for r in STRATEGY_RULES if r["id"] != rule_id]
    return {"status": "deleted"}
