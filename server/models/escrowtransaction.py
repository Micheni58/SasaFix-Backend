# models/escrowtransaction.py - Stercy
# — id, booking_id (foreign key to Booking), 
# client_id (foreign key to User), 
# provider_id (foreign key to ServiceProvider), gross_amount, 
# commission_rate, commission_amount, net_amount, type (payment, payout, refund), 
# status (pending, completed, failed), mpesa_reference, created_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id = Column(Integer, primary_key=True, index=True)
    gross_amount = Column(Integer)
    commission_rate = Column(Integer)
    
    