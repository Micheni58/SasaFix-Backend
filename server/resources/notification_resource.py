# notification_resource.py - Caleb
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.database import get_db  # database.py      

router = APIRouter()

@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    # Placeholder for fetching notifications from the database
    return {"message": "List of notifications will be returned here."}