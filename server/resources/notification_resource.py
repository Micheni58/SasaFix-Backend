# notification_resource.py - Caleb
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.services import serviceprovider_service
from server.core.database import get_db  # database.py      

router = APIRouter()

@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    return serviceprovider_service.get_notifications(db)    
