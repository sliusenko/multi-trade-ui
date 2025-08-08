from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.db import database
from app.auth.dependencies import get_db
from models import Role, Permission
from schemas import RoleOut, PermissionOut

router = APIRouter(prefix="/api/config", tags=["Config"])

@router.get("/roles", response_model=list[RoleOut])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.get("/permissions", response_model=list[PermissionOut])
def get_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()