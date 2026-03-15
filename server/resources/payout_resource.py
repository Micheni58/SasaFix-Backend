from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.database import get_db  # database.py

router = APIRouter()

@router.get("/payouts")
def get_payouts(db: Session = Depends(get_db)):
    # Placeholder for fetching payouts from the database
    return {"message": "List of payouts will be returned here."}