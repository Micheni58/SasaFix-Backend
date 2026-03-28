# schemas/booking_schema.py - Caleb

from datetime import date, datetime, time
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# What the client sends when creating a booking
class BookingCreate(BaseModel):
    client_id: int
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    client_id: Optional[int] = None
    service_provider_id: Optional[int] = None
    service_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_date: Optional[date] = None
    scheduled_start_time: Optional[time] = None
    scheduled_end_time: Optional[time] = None
    location: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    amount: Optional[float] = Field(None, gt=0)
    status: Optional[BookingStatus] = None


# What is sent when updating a booking status
class BookingStatusUpdate(BaseModel):
    status: BookingStatus


# What is sent when rescheduling a booking
class BookingReschedule(BaseModel):
    scheduled_date: date
    scheduled_start_time: time
    scheduled_end_time: time
