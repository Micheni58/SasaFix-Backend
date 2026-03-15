# models/subscription.py - Stercy
# id, provider_id (foreign key to ServiceProvider), 
# plan (free or premium), commission_rate (10 or 5), price_paid, 
# start_date, end_date, is_active, created_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    