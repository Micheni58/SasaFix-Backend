# models/wallet.py - Stercy
# id, user_id (foreign key to User), balance, currency (KES), updated_at, created_at
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from server.core.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="KES")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
