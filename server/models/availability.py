# models/availability.py - Jeremy
#  id, service_provider_id (foreign key to ServiceProvider),
#  day_of_week (Monday to Sunday), 
# start_time, end_time, is_booked, 
# created_at, updated_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base   

class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String)  
    start_time = Column(String)  
    end_time = Column(String)  

    def __repr__(self):
        return f"<Availability(id={self.id}, day_of_week='{self.day_of_week}', start_time='{self.start_time}', end_time='{self.end_time}')>"