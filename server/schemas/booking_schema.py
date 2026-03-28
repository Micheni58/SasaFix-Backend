# schemas/booking_schema.py - Caleb

from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# What the client sends when creating a booking
class BookingCreate(BaseModel):
    service_provider_id: int
    service_name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_date: date
    scheduled_start_time: time
    scheduled_end_time: time
    location: str = Field(..., max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    amount: float = Field(..., gt=0)  # must be greater than 0


# What the API sends back in responses
class BookingResponse(BaseModel):
    id: int
    client_id: int
    service_provider_id: int
    service_name: str
    description: Optional[str]
    scheduled_date: date
    scheduled_start_time: time
    scheduled_end_time: time
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: BookingStatus
    amount: float
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# What is sent when updating a booking status
class BookingStatusUpdate(BaseModel):
    status: BookingStatus


# What is sent when rescheduling a booking
class BookingReschedule(BaseModel):
    scheduled_date: date
    scheduled_start_time: time
    scheduled_end_time: time