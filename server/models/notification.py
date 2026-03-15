# models/notification.py - Caleb
#  id, user_id (foreign key to User), 
# type (booking, payment, message), title, body, 
# is_read, related_booking_id (nullable foreign key to Booking), created_at
import datetime

from sqlalchemy import Column, Integer, String, ForeignKey,Boolean, DateTime
from server.core.database import Base   
class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    title = Column(String)
    body = Column(String)
    is_read = Column(Boolean, default=False)
    related_booking_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Availability(id={self.id}, type='{self.type}', title='{self.title}', is_read={self.is_read})>"