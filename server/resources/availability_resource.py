# availability_resource.py - Jeremy
# `
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.database import get_db  # database.py  

router = APIRouter()

@router.get("/availabilities")
def get_availabilities(db: Session = Depends(get_db)):
    # Placeholder for fetching availabilities from the database
    return {"message": "List of availabilities will be returned here."}