from jose import JWTError, jwt
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

SECRET_KEY = "supersecret"      # Винеси в .env
# # Краще зберігати в .env
# SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# Краще зберігати в .env
#SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
