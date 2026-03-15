# providerservice_resource.py - Jeremy

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.database import get_db  # database.py

router = APIRouter()

@router.get("/providerservices")
def get_provider_services(db: Session = Depends(get_db)):
    # Placeholder for fetching provider services from the database
    return {"message": "List of provider services will be returned here."}