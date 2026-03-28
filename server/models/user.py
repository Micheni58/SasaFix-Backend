# models/user.py - Jeremy
# id, first_name,
# last_name, email, phone_number, password_hash,
# role (client or service_provider or admin),
# profile_photo_url, location, created_at, updated_at,
# is_active, is_suspended
import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from server.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Just define the column, don't hash here

    # Add these missing fields
    full_name = Column(String, index=True)
    role = Column(String, default='client')  # 'client', 'service_provider', 'admin'

    # Optional fields from your comment
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, unique=True, index=True)
    profile_photo_url = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)

    client_bookings = relationship(
        "Booking",
        back_populates="client",
        foreign_keys="Booking.client_id",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, full_name='{self.full_name}', email='{self.email}', role='{self.role}')>"
