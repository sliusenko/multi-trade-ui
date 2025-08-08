from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_db
from app import models
from app.schemas import user_config
from app.services.db import database
from typing import Optional, List
from app.dependencies import get_current_user
from app.models import users


router = APIRouter(prefix="/api/config/users", tags=["User Config"])


@router.get("/", response_model=List[user_config.UserOut])
async def get_users(current_user_id: int = Depends(get_current_user)):
    """Отримати всіх користувачів"""
    query = select(users)  # SQLAlchemy Core
    rows = await database.fetch_all(query)
    return [user_config.UserOut(**dict(row)) for row in rows]


@router.post("/", response_model=user_config.UserOut)
async def create_user(user: user_config.UserCreate, db: AsyncSession = Depends(get_db)):
    """Створити нового користувача"""
    db_user = models.user(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=user_config.UserOut)
async def update_user(user_id: int, user: user_config.UserUpdate, db: AsyncSession = Depends(get_db)):
    """Оновити користувача"""
    result = await db.execute(select(models.user).where(models.user.user_id == user_id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Видалити користувача"""
    result = await db.execute(select(models.User).where(models.User.user_id == user_id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    return {"detail": "User deleted"}
