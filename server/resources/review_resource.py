# review_resource.py - Caleb
# Review resource for handling review-related API endpoints. 
# This includes fetching reviews for service providers, creating new reviews, and managing review data. 
# The resource interacts with the review service layer to perform database operations and business logic related to reviews.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.services import serviceprovider_service
from server.core.database import get_db  # database.py

router = APIRouter()

@router.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    return serviceprovider_service.get_reviews(db)