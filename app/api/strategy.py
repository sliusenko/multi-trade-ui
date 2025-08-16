# app/api/strategy.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.strategy import StrategyRuleCreate, StrategyRuleUpdate, StrategyRuleResponse
from app.dependencies import get_current_user, is_admin_user, _resolve_user_scope
from sqlalchemy import select, update, delete, text, distinct, and_
from app.services.db import database
from app.models import strategy_rules, user_active_pairs

router = APIRouter(prefix="/api/strategy_rules", tags=["Strategy Rules"])

# ---- helpers ----
_ALL_TOKENS = {"", "all", "any", "all pairs", "all users", "all exchanges", "null", "-"}

def _normalize_exchange(ex: str | None) -> str | None:
    if ex is None:
        return None
    ex_norm = ex.strip().lower()
    return None if ex_norm in _ALL_TOKENS else ex_norm

def _normalize_pair(p: str | None) -> str | None:
    if p is None:
        return None
    p_norm = p.strip()
    # приймаємо як плейсхолдери: "", "all", "All Pairs", "-", "null"
    return None if p_norm.lower() in _ALL_TOKENS else p_norm.upper()

# ---- GET (list) ----
@router.get("", response_model=List[StrategyRuleResponse])
async def list_rules(
    exchange: str | None = Query(None),
    pair: str | None = Query(None),
    user_id: int | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    ex = _normalize_exchange(exchange)   
    pr = _normalize_pair(pair)

    uid = _resolve_user_scope(user_id, current_user_id, admin)

    # Базовий селект по таблиці правил
    stmt = select(strategy_rules)

    # Якщо у strategy_rules є колонка user_id — фільтруємо нею
    if "user_id" in strategy_rules.c:
        stmt = stmt.where(strategy_rules.c.user_id == uid)

    if ex is not None and "exchange" in strategy_rules.c:
        stmt = stmt.where(strategy_rules.c.exchange == ex)

    if pr is not None and "pair" in strategy_rules.c:
        stmt = stmt.where(strategy_rules.c.pair == pr)

    # (опційно) сортування, якщо є поле id або priority
    if "priority" in strategy_rules.c:
        stmt = stmt.order_by(strategy_rules.c.priority)
    elif "id" in strategy_rules.c:
        stmt = stmt.order_by(strategy_rules.c.id)

    rows = await database.fetch_all(stmt)   # ← ти це пропустив
    return [dict(r) for r in rows]

@router.get("", response_model=List[StrategyRuleResponse])
@router.get("/", response_model=List[StrategyRuleResponse])
async def get_rules(current_user_id: int = Depends(get_current_user)):
    q = select(strategy_rules).where(strategy_rules.c.user_id == current_user_id)
    rows = await database.fetch_all(q)
    return [StrategyRuleResponse(**dict(r)) for r in rows]

# ---- POST (create) ----
@router.post("", response_model=StrategyRuleResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=StrategyRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: StrategyRuleCreate, current_user_id: int = Depends(get_current_user)):
    data = rule.dict()
    data["user_id"] = current_user_id
    inserted_id = await database.execute(strategy_rules.insert().values(**data))
    row = await database.fetch_one(select(strategy_rules).where(strategy_rules.c.id == inserted_id))
    return StrategyRuleResponse(**dict(row))

# ---- PUT/PATCH (update) ----
@router.put("/{rule_id}", response_model=StrategyRuleResponse)
@router.patch("/{rule_id}", response_model=StrategyRuleResponse)
async def update_rule(
    rule_id: int,
    rule: StrategyRuleUpdate,
    user_id: int | None = Query(None),
    current_user_id: int = Depends(get_current_user),
    admin: bool = Depends(is_admin_user),
):
    # 1) Визначаємо, в чиєму scope працюємо
    uid = _resolve_user_scope(user_id, current_user_id, admin)

    # 2) Читаємо правило в межах цього користувача
    current = await database.fetch_one(
        select(strategy_rules).where(
            strategy_rules.c.id == rule_id,
            strategy_rules.c.user_id == uid,
        )
    )
    if not current:
        # не розкриваємо, чи існує ресурс взагалі
        raise HTTPException(status_code=404, detail="Rule not found")

    # 3) Формуємо оновлення (без можливості змінити власника)
    values = rule.dict(exclude_unset=True)
    values.pop("user_id", None)  # забороняємо переносити правило між користувачами

    if not values:
        # нічого оновлювати — повертаємо поточний стан
        return StrategyRuleResponse(**dict(current))

    # 4) Оновлюємо в межах scope (id + user_id)
    await database.execute(
        update(strategy_rules)
        .where(
            strategy_rules.c.id == rule_id,
            strategy_rules.c.user_id == uid,
        )
        .values(**values)
    )

    # 5) Повертаємо свіже значення
    row = await database.fetch_one(
        select(strategy_rules).where(
            strategy_rules.c.id == rule_id,
            strategy_rules.c.user_id == uid,
        )
    )
    return StrategyRuleResponse(**dict(row))

# ---- DELETE ----
@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: int, current_user_id: int = Depends(get_current_user)):
    await database.execute(
        delete(strategy_rules).where(strategy_rules.c.id == rule_id, strategy_rules.c.user_id == current_user_id)
    )

@router.get("/filters/user-active-pairs")
async def get_filters(
    user_id: int | None = Query(None),
    exchange: str | None = Query(None),
):
    # --- users ---
    stmt_users = select(distinct(user_active_pairs.c.user_id))
    rows_users = await database.fetch_all(stmt_users)
    users = sorted([r[0] for r in rows_users])

    # --- exchanges (звужуємо за user_id, якщо заданий) ---
    stmt_ex = select(distinct(user_active_pairs.c.exchange))
    if user_id is not None:
        stmt_ex = stmt_ex.where(user_active_pairs.c.user_id == user_id)
    rows_ex = await database.fetch_all(stmt_ex)
    exchanges = sorted([r[0] for r in rows_ex])

    # --- pairs (звужуємо за user_id та exchange, якщо задані) ---
    stmt_pairs = select(distinct(user_active_pairs.c.pair))
    conds = []
    if user_id is not None:
        conds.append(user_active_pairs.c.user_id == user_id)
    if exchange:
        conds.append(user_active_pairs.c.exchange == exchange)
    if conds:
        stmt_pairs = stmt_pairs.where(and_(*conds))
    rows_pairs = await database.fetch_all(stmt_pairs)
    pairs = sorted([r[0] for r in rows_pairs])

    return {"users": users, "exchanges": exchanges, "pairs": pairs}
