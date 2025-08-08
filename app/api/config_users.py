from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_db
from app import models
from app.schemas import user_config
from app.services.db import database
from typing import Optional, List
from app.dependencies import get_current_user
from app.auth.jwt_handler import hash_password
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

    user_data = user.dict()
    password_hash = hash_password(user_data.pop("password"))  # забираємо plain password

    insert_query = models.users.insert().values(**user_data, password_hash=password_hash)
    result = await db.execute(insert_query)
    await db.commit()

    # Отримати нового користувача
    user_id = result.inserted_primary_key[0]
    query = select(models.users).where(models.users.c.user_id == user_id)
    new_user = await db.execute(query)
    row = new_user.fetchone()
    return user_config.UserOut(**dict(row))

from app.auth.jwt_handler import hash_password

@router.put("/{user_id}", response_model=user_config.UserOut)
async def update_user(
    user_id: int,
    updated_data: user_config.UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Оновити дані користувача"""

    update_data = updated_data.dict(exclude_unset=True)

    # Хешування пароля, якщо його передано
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    update_query = (
        update(models.users)
        .where(models.users.c.user_id == user_id)
        .values(**update_data)
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(update_query)
    await db.commit()

    # Отримати оновленого користувача
    query = select(models.users).where(models.users.c.user_id == user_id)
    result = await db.execute(query)
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return user_config.UserOut(**dict(row))

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Видалити користувача"""
    query = select(models.users).where(models.users.c.user_id == user_id)
    result = await db.execute(query)
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_query = models.users.delete().where(models.users.c.user_id == user_id)
    await db.execute(delete_query)
    await db.commit()

    return {"detail": "User deleted"}

