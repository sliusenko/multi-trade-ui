from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.db import database
from app.models import users
from sqlalchemy import select

# Простий варіант з токеном в Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def is_admin_user(current_user=Depends(get_current_user)) -> bool:
    """
    Перевіряє, чи користувач має права адміністратора.
    Повертає True/False.
    """
    # якщо get_current_user вже повертає user dict:
    if isinstance(current_user, dict):
        return bool(current_user.get("is_admin"))

    # якщо повертає user_id:
    stmt = select(users.c.is_admin).where(users.c.id == current_user)
    row = await database.fetch_one(stmt)
    return bool(row["is_admin"]) if row else False

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Тут можна робити перевірку токена, поки повернемо фіктивного користувача
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return 46205214 # Наприклад, user_id = 1
