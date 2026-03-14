# models/booking.py - Caleb
# id, client_id (foreign key to User), 
# provider_id (foreign key to ServiceProvider), 
# service_name, description, location_address, 
# latitude, longitude, scheduled_date, scheduled_start_time, 
# scheduled_end_time, status (pending, accepted, in_progress, 
# completed, cancelled), amount, created_at, updated_at
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from server.core.database import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String)
    description = Column(String)
    location_address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    scheduled_date = Column(String)  
    scheduled_start_time = Column(String)  
    scheduled_end_time = Column(String)  
    status = Column(String)  
    amount = Column(Float)

    def __repr__(self):
        return f"<Booking(id={self.id}, service_name='{self.service_name}', status='{self.status}', amount={self.amount})>"