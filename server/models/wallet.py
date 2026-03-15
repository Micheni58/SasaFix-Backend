# models/wallet.py - Stercy
# id, user_id (foreign key to User), balance, currency (KES), updated_at, created_at
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from server.core.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    
