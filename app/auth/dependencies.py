from app.services.db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

async def get_db():
    async with SessionLocal() as session:
        yield session

# Простий варіант з токеном в Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Тут можна робити перевірку токена, поки повернемо фіктивного користувача
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return 46205214 # Наприклад, user_id = 1

def _resolve_user_scope(
    requested_user_id: int | None,
    current_user_id: int,
    is_admin: bool,
) -> int:
    # якщо фронт шле user_id=0 або "all" — трактуємо як None
    if requested_user_id in (None, 0):
        return current_user_id
    if requested_user_id == current_user_id or is_admin:
        return requested_user_id
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

# app/dependencies.py
def resolve_user_scope(requested_user_id: int | None, current_user_id: int, is_admin: bool) -> int:
    return _resolve_user_scope(requested_user_id, current_user_id, is_admin)
