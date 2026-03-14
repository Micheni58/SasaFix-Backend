# schemas/availability_schema.py - Jeremy

from pydantic import BaseModel, Field

class AvailabilityCreate(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str

class AvailabilityResponse(AvailabilityCreate):
    id: int
    class Config:
        from_attributes = True
    years_of_experience: int
    hourly_rate: float  
