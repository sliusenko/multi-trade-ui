from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.db import database
from app.models import users
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return 46205214  # Тимчасово фіксований user_id

async def is_admin_user(current_user=Depends(get_current_user)) -> bool:
    uid = current_user["user_id"] if isinstance(current_user, dict) else int(current_user)
    row = await database.fetch_one(select(users.c.role).where(users.c.user_id == uid))
    return str(row["role"]).lower() in {"admin", "owner", "superuser"} if row else False

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
