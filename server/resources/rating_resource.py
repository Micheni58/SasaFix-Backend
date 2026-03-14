# rating_resource.py - Caleb
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.services import rating_service
from server.core.database import get_db  # database.py  

router = APIRouter()

@router.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    return rating_service.get_ratings(db)