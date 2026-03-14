# models/rating.py - Caleb
#  id, booking_id (foreign key to Booking), 
# client_id (foreign key to User), 
# provider_id (foreign key to ServiceProvider), 
# score (1 to 5), created_at, updated_at

from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating_value = Column(Integer)  
    review = Column(String)  

    def __repr__(self):
        return f"<Rating(id={self.id}, rating_value={self.rating_value}, review='{self.review}')>"