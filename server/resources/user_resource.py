from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.services import user_service
from server.core.database import get_db  # database.py

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)