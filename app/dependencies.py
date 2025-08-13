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
    if isinstance(current_user, dict):
        return bool(current_user.get("is_admin"))

    stmt = select(users.c.is_admin).where(users.c.id == current_user)
    row = await database.fetch_one(stmt)
    return bool(row["is_admin"]) if row else False
