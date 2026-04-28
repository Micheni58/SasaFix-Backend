# models/booking.py - Dev 3
import enum
from sqlalchemy import Column, DateTime, Date, Time, Float, ForeignKey, Integer, String, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy import func
from server.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    service_provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=True)
    scheduled_start_time = Column(Time, nullable=True)
    scheduled_end_time = Column(Time, nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(SAEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    client = relationship("User", back_populates="client_bookings")
    service_provider = relationship("ServiceProvider", back_populates="bookings")

    def __repr__(self):
        return (
            f"<Booking(id={self.id}, service_name='{self.service_name}', "
            f"status='{self.status}', amount={self.amount})>"
        )

    def is_active(self):
        return self.status in {
            BookingStatus.PENDING,
            BookingStatus.ACCEPTED,
            BookingStatus.IN_PROGRESS,
        }

    def is_completed(self):
        return self.status == BookingStatus.COMPLETED

    def can_be_cancelled(self):
        return self.status not in {BookingStatus.COMPLETED, BookingStatus.CANCELLED}

    def set_status(self, new_status: BookingStatus):
        if new_status not in BookingStatus:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
