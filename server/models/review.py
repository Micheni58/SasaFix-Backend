# models/review.py - Caleb
#  id, booking_id (foreign key to Booking), 
# client_id (foreign key to User), provider_id (foreign key to ServiceProvider), 
# rating (1 to 5), comment, provider_response, is_flagged, 
# created_at, updated_at
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from server.core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)  
    comment = Column(String)  
    provider_response = Column(String)  
    is_flagged = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, is_flagged={self.is_flagged})>"