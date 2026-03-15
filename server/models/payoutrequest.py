# models/payoutrequest.py - Stercy
#  id, provider_id (foreign key to ServiceProvider), amount, 
# payout_method (mpesa or bank), payout_destination (phone number or account number), 
# status (pending, approved, processing, completed, held), admin_note, 
# requested_at, processed_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    status = Column(String)  # pending, approved, rejected
    created_at = Column(String)

    def __repr__(self):
        return f"<PayoutRequest(id={self.id}, amount={self.amount}, status='{self.status}')>"