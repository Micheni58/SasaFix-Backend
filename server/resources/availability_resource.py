# availability_resource.py - Jeremy
# `
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.services import serviceprovider_service
from server.core.database import get_db  # database.py  

router = APIRouter()

@router.get("/service_providers")
def get_service_providers(db: Session = Depends(get_db)):
    return serviceprovider_service.get_service_providers(db)    